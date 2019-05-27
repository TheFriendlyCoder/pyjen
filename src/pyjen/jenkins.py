"""Primitives for interacting with the main Jenkins dashboard"""
import logging
from requests.exceptions import RequestException
from pyjen.view import View
from pyjen.node import Node
from pyjen.job import Job
from pyjen.user import User
from pyjen.queue import Queue
from pyjen.plugin_manager import PluginManager
from pyjen.utils.jenkins_api import JenkinsAPI
from pyjen.utils.helpers import create_view, create_job


class Jenkins(object):
    """Python wrapper managing the Jenkins primary dashboard

    Generally you should use this class as the primary entry point to the PyJen
    APIs. Finer grained control of each aspect of the Jenkins dashboard is then
    provided by the objects exposed by this class including:

    * :class:`~.view.View` - abstraction for a view on the dashboard, allowing
      jobs to be filtered based on different criteria like job name.
    * :class:`~.job.Job` - abstraction for a Jenkins job, allowing manipulation
      of job settings and controlling builds of those jobs
    * :class:`~.build.Build` - abstraction for an instance of a build of a
                               particular job

    **Example:** finding a job ::

        j = pyjen.Jenkins('http://localhost:8080')
        job = j.find_job('My Job')
        if job is None:
            print ('no job by that name found')
        else:
            print ('job ' + job.name + ' found')

    **Example:** find the build number of the last good build of the first job
                 on the default view ::

        j = pyjen.Jenkins('http://localhost:8080/')
        v = j.get_default_view()
        jobs = v.get_jobs()
        lgb = jobs[0].last_good_build
        print ('last good build of the first job in the default view is ' +
            lgb.get_build_number())

    :param str url: Full HTTP URL to the main Jenkins dashboard
    :param tuple credentials:
        Optional 2-tuple containing the username and password / api key to
        authenticate with. If not provided, anonymous access will be assumed
    :param ssl_cert:
        Passed directly to the requests library when authenticating to the
        remote server. Maybe be a boolean indicating whether SSL verification
        is enabled or disabled, or may be a path to a certificate authority
        bundle.
    """

    def __init__(self, url, credentials=None, ssl_cert=True):
        super(Jenkins, self).__init__()
        self._log = logging.getLogger(__name__)
        self._api = JenkinsAPI(url, credentials, ssl_cert)

    @property
    def connected(self):
        """make sure the connection to the Jenkins REST API was successful

        :returns: True if connected, false if not
        :rtype: :class:`bool`
        """
        try:
            if self._api.jenkins_headers:
                return True
            return False
        except RequestException as err:
            self._log.error("Jenkins connection failed: %s.", err)
            return False

    @property
    def version(self):
        """Gets the version of Jenkins pointed to by this object

        :return: Version number of the currently running Jenkins instance
        :rtype: :class:`tuple`
        """
        return self._api.jenkins_version

    @property
    def is_shutting_down(self):
        """Is the Jenkins master is in the process of shutting down.

        :returns:
            If the Jenkins master is preparing to shutdown
            (ie: in quiet down state), return True, otherwise returns False.
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()

        return data['quietingDown']

    @property
    def nodes(self):
        """gets the list of nodes (aka: agents) managed by this Jenkins master

        :returns: list of 0 or more Node objects managed by this Jenkins master
        :rtype: :class:`list` of :class:`~.node.Node` objects
        """
        data = self._api.get_api_data(target_url=self._api.url + "computer/")
        nodes = data['computer']
        retval = []
        for cur_node in nodes:
            if cur_node['displayName'] == 'master':
                node_url = self._api.url + 'computer/(master)'
            else:
                node_url = self._api.url + 'computer/' + cur_node['displayName']

            retval.append(Node(self._api.clone(node_url)))

        return retval

    @property
    def default_view(self):
        """returns a reference to the primary / default Jenkins view

        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view.

        :returns: object that manages the default Jenkins view
        :rtype: :class:`~.view.View`
        """
        data = self._api.get_api_data()

        return View.instantiate(data['primaryView'], self._api)

    @property
    def views(self):
        """Gets a list of all views directly managed by the Jenkins dashboard

        To retrieve all views managed by this Jenkins instance, including
        recursing into views that support sub-views, see the
        :py:meth:`.all_views` property

        :returns: list of one or more views defined on this Jenkins instance.
        :rtype: :class:`list` of :class:`~.view.View` objects
        """
        retval = list()

        data = self._api.get_api_data()

        for cur_view in data['views']:
            retval.append(View.instantiate(cur_view, self._api))

        return retval

    @property
    def jobs(self):
        """Gets all jobs managed by this Jenkins instance

        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._api.get_api_data(query_params="depth=0")

        retval = list()
        for j in data['jobs']:
            retval.append(Job.instantiate(j, self._api))

        return retval

    def _recursively_find_jobs(self, obj):
        """Recursively locates all jobs managed by an arbitrary Jenkins object

        :param obj:
            An arbitrary Jenkins object which may contain jobs. The given object
            may be one of any number of PyJen plugins, but it must expose
            a 'jobs' property which can be used to load a list of jobs
            managed by the object
        :rtype: :class:`list` of :class:`~.job.Job` objects"""
        retval = list()
        for cur_job in obj.jobs:
            retval.append(cur_job)
            if isinstance(getattr(type(cur_job), "jobs", None), property):
                retval.extend(self._recursively_find_jobs(cur_job))
        return retval

    @property
    def all_jobs(self):
        """Gets all jobs managed by this Jenkins instance, recursively

        Unlike the :meth:`jobs` method, this method attempts to expose jobs
        which are managed by custom jobs created from third party plugins which
        support nesting jobs under sub-folders / sub-paths. Any job which
        exposes a custom 'jobs' property.

        :rtype: :class:`list` of :class:`~.job.Job` objects"""
        return self._recursively_find_jobs(self)

    def prepare_shutdown(self):
        """Starts a "quiet down" and prevents new builds from executing

        Analogous to the "Prepare for Shutdown" link on the Manage Jenkins
        configuration page

        You can cancel a previous requested shutdown using the
        :py:meth:`.cancel_shutdown` method
        """
        self._api.post(self._api.url + 'quietDown')

    def cancel_shutdown(self):
        """Cancels a previous scheduled shutdown sequence

        Cancels a shutdown operation initiated by the
        :py:meth:`.prepare_shutdown` method
        """
        self._api.post(self._api.url + 'cancelQuietDown')

    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job

        .. seealso: :py:meth:`.get_job`

        :param str job_name: the name of the job to search for
        :returns:
            If a job with the specified name can be found, and object to manage
            the job will be returned, otherwise None
        :rtype: :class:`~.job.Job`
        """
        data = self._api.get_api_data()

        for cur_job in data['jobs']:
            if cur_job['name'] == job_name:
                return Job.instantiate(cur_job, self._api)

        return None

    def find_view(self, view_name):
        """Searches views for a specific one

        .. seealso: :py:meth:`.get_view`

        :param str view_name: the name of the view to search for
        :returns:
            If a view with the specified name can be found, an object to manage
            the view will be returned, otherwise None
        :rtype: :class:`~.view.View`
        """
        data = self._api.get_api_data()

        for cur_view in data['views']:
            temp_view = View.instantiate(cur_view, self._api)
            if temp_view.name == view_name:
                return temp_view

        return None

    def create_view(self, view_name, view_class):
        """Creates a new view on the Jenkins dashboard

        :param str view_name:
            the name for this new view
            This name should be unique, different from any other views currently
            managed by the Jenkins instance
        :param view_class:
            PyJen plugin class associated with the type of view to be created
        :returns: An object to manage the newly created view
        :rtype: :class:`~.view.View`
        """

        create_view(self._api, view_name, view_class)
        retval = self.find_view(view_name)
        assert retval is not None
        return retval

    def create_job(self, job_name, job_class):
        """Creates a new job on the Jenkins dashboard

        :param str job_name:
            the name for this new job
            This name should be unique, different from any other jobs currently
            managed by the Jenkins instance
        :param job_class:
            PyJen plugin class associated with the type of job to be created
        :returns: An object to manage the newly created job
        :rtype: :class:`~.job.Job`
        """
        create_job(self._api, job_name, job_class)

        retval = self.find_job(job_name)
        assert retval is not None
        return retval

    def find_user(self, username):
        """Locates a user with the given username on this Jenkins instance

        :param str username: name of user to locate
        :returns:
            reference to Jenkins object that manages this users information.
        :rtype: :class:`~.user.User` or None if user not found
        """
        # TODO: Rework 'users' property to cache the user name for all users in
        #       one query, so we can rework this implementation to simply call
        #       self.users then iterate through them all to find the one
        #       we're looking for. Then we don't have to guess the URL.
        new_url = self._api.url + "user/" + username
        try:
            retval = User(self._api.clone(new_url))
            assert retval.user_id == username
            return retval
        except RequestException:
            return None

    def find_node(self, nodename):
        """Locates a Jenkins build agent with the given name

        :param str nodename: name of node to locate
        :returns:
            reference to Jenkins object that manages this node's information.
        :rtype: :class:`~.node.Node` or None if node not found
        """
        if nodename == "master":
            temp_nodename = "(master)"
        else:
            temp_nodename = nodename

        # TODO: Rework 'nodes' property to cache the node name for all nodes in
        #       one query, so we can rework this implementation to simply call
        #       self.nodes then iterate through them all to find the one
        #       we're looking for. Then we don't have to guess the URL.

        new_url = self._api.url + "computer/" + temp_nodename
        try:
            retval = Node(self._api.clone(new_url))
            assert retval.name == nodename
            return retval
        except RequestException:
            return None

    @property
    def plugin_manager(self):
        """object which manages the plugins installed on this Jenkins

        :returns:
            reference to Jenkins object that manages plugins on this instance
        :rtype: :class:`~.plugin_manager.PluginManager`
        """
        return PluginManager(self._api.clone(self._api.url + 'pluginManager'))

    @property
    def build_queue(self):
        """object that describes / manages the queued builds

        :rtype: :class:`~.queue.Queue`
        """
        return Queue(self._api.clone(self._api.url + 'queue'))


if __name__ == '__main__':  # pragma: no cover
    pass
