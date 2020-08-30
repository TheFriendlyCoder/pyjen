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


class Jenkins:
    """Python wrapper managing the Jenkins primary dashboard

    Generally you should use this class as the primary entry point to the PyJen
    APIs. Finer grained control of each aspect of the Jenkins dashboard is then
    provided by the objects exposed by this class including
    :class:`~.view.View`, :class:`~.job.Job` and :class:`~.build.Build`.
    """

    def __init__(self, url, credentials=None, ssl_cert=True):
        """
        Args:
            url (str):
                Full HTTP URL to the main Jenkins dashboard
            credentials (tuple):
                Optional 2-tuple containing the username and password / api
                key to authenticate with. If not provided, anonymous access
                will be assumed
            ssl_cert (str):
                Passed directly to the requests library when authenticating to
                the remote server. Maybe be a boolean indicating whether SSL
                verification is enabled or disabled, or may be a path to a
                certificate authority bundle.
        """
        super().__init__()
        self._log = logging.getLogger(__name__)
        self._api = JenkinsAPI(url, credentials, ssl_cert)

    @property
    def connected(self):
        """bool: True if API still connected to the service, False if not"""
        try:
            if self._api.jenkins_headers:
                return True
            return False
        except RequestException as err:
            self._log.error("Jenkins connection failed: %s.", err)
            return False

    @property
    def version(self):
        """tuple: version of Jenkins service, parsed into a tuple of integers"""
        return self._api.jenkins_version

    @property
    def is_shutting_down(self):
        """bool: True if the Jenkins master is scheduled for a shutdown, False
        if not"""
        data = self._api.get_api_data()

        return data['quietingDown']

    @property
    def nodes(self):
        """list (Node): list of build agents"""
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
        """View: the primary / default Jenkins view

        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view, but this may be
        customized by the user at runtime.
        """
        data = self._api.get_api_data()

        return View.instantiate(data['primaryView'], self._api)

    @property
    def views(self):
        """list (View): all views directly managed by this Jenkins instance"""
        retval = list()

        data = self._api.get_api_data()

        for cur_view in data['views']:
            retval.append(View.instantiate(cur_view, self._api))

        return retval

    @property
    def jobs(self):
        """list (Job): all jobs managed by this Jenkins instance"""
        data = self._api.get_api_data(query_params="depth=0")

        retval = list()
        for j in data['jobs']:
            retval.append(Job.instantiate(j, self._api))

        return retval

    def _recursively_find_jobs(self, obj):
        """Recursively locates all jobs managed by an arbitrary Jenkins object

        Args:
            obj:
                An arbitrary Jenkins object which may contain jobs. The given
                object may be one of any number of PyJen plugins, but it must
                expose a 'jobs' property which can be used to load a list of
                jobs managed by the object

        Returns:
            list (Job):
                list of jobs nested within other jobs, recursively
        """
        retval = list()
        for cur_job in obj.jobs:
            retval.append(cur_job)
            if isinstance(getattr(type(cur_job), "jobs", None), property):
                retval.extend(self._recursively_find_jobs(cur_job))
        return retval

    @property
    def all_jobs(self):
        """list (Job): all jobs managed by this Jenkins instance, recursively

        Unlike the :meth:`jobs` method, this method attempts to expose jobs
        which are managed by custom jobs created from third party plugins which
        support nesting jobs under sub-folders / sub-paths. Any job which
        exposes a custom 'jobs' property."""
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

        Some plugins allow jobs to be nested within other jobs. To perform a
        recursive search across all such entities, see :py:meth:`.all_jobs`.

        Args:
            job_name (str): the name of the job to search for

        Returns:
            Job:
                If a job with the specified name can be found, and object to
                manage the job will be returned, otherwise None
        """
        data = self._api.get_api_data()

        for cur_job in data['jobs']:
            if cur_job['name'] == job_name:
                return Job.instantiate(cur_job, self._api)

        return None

    def find_view(self, view_name):
        """Searches views for a specific one

        Args:
            view_name (str): the name of the view to search for

        Returns:
            View:
                If a view with the specified name can be found, an object to
                manage the view will be returned, otherwise returns None
        """
        data = self._api.get_api_data()

        for cur_view in data['views']:
            temp_view = View.instantiate(cur_view, self._api)
            if temp_view.name == view_name:
                return temp_view

        return None

    def create_view(self, view_name, view_class):
        """Creates a new view on the Jenkins dashboard

        Args:
            view_name (str):
                The name for this new view. This name should be unique,
                different from any other views currently managed by the Jenkins
                instance
            view_class:
                PyJen plugin class associated with the type of view to be
                created

        Returns:
            View: An object to manage the newly created view
        """

        create_view(self._api, view_name, view_class)
        retval = self.find_view(view_name)
        assert retval is not None
        return retval

    def create_job(self, job_name, job_class):
        """Creates a new job on the Jenkins dashboard

        Args:
            job_name (str):
                The name for this new job. This name should be unique,
                different from any other jobs currently managed by the
                Jenkins instance
            job_class:
                PyJen plugin class associated with the type of job to be created

        Returns:
            Job: An object to manage the newly created job
        """
        create_job(self._api, job_name, job_class)

        retval = self.find_job(job_name)
        assert retval is not None
        return retval

    def find_user(self, username):
        """Locates a user with the given username on this Jenkins instance

        Args:
            username (str): name of user to locate

        Returns:
            User:
                reference to Jenkins object that manages this users information,
                or None if no user with the specified name can be found
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

        Args:
            nodename (str): name of node to locate

        Returns:
            Node:
                reference to Jenkins object that manages this node's
                information, or None if no node with the given name can be
                found
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
        """PluginManager: interface for managing the plugins installed on this
        Jenkins instance"""
        return PluginManager(self._api.clone(self._api.url + 'pluginManager'))

    @property
    def build_queue(self):
        """Queue: interface for managing the Jenkins build queue"""
        return Queue(self._api.clone(self._api.url + 'queue'))


if __name__ == "__main__":  # pragma: no cover
    pass
