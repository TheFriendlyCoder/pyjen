"""Primitives for interacting with the main Jenkins dashboard"""
import json
import logging
from requests.exceptions import RequestException
from pyjen.view import View
from pyjen.node import Node
from pyjen.job import Job
from pyjen.user import User
from pyjen.plugin_manager import PluginManager
from pyjen.utils.datarequester import DataRequester
from pyjen.utils.user_params import JenkinsConfigParser


class Jenkins(object):
    """Python wrapper managing the Jenkins primary dashboard

    Generally you should use this class as the primary entry
    point to the PyJen APIs. Finer grained control of each
    aspect of the Jenkins dashboard is then provided by the
    objects exposed by this class including:

    * :class:`~.view.View` - abstraction for a view on the dashboard, allowing
      jobs to be filtered based on different criteria like job name.
    * :class:`~.job.Job` - abstraction for a Jenkins job, allowing manipulation
      of job settings and controlling builds of those jobs
    * :class:`~.build.Build` - abstraction for an instance of a build of a
      particular job

    **Example:** finding a job ::

        j = Jenkins.easy_connect('http://localhost:8080')
        job = j.find_job('My Job')
        if job is None:
            print ('no job by that name found')
        else:
            print ('job ' + job.name + ' found')

    **Example:** find the build number of the last good build of the first job on the default view ::

        j = pyjen.Jenkins.easy_connect('http://localhost:8080/')
        v = j.get_default_view()
        jobs = v.get_jobs()
        lgb = jobs[0].get_last_good_build()
        print ('last good build of the first job in the default view is ' + lgb.get_build_number())
    """

    def __init__(self, data_io_controller):
        """
        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        """
        self._controller = data_io_controller
        self._log = logging.getLogger(__name__)

    @staticmethod
    def easy_connect(url, credentials=None, ssl_verify=False):
        """Factory method to simplify creating connections to Jenkins servers

        :param str url:
            Full URL of the Jenkins instance to connect to. Must be
            a valid running Jenkins instance.
        :param tuple credentials:
            A 2-element tuple with the username and password for authenticating to the URL
            If omitted, credentials will be loaded from any pyjen config files found on the system
            If no credentials can be found, anonymous access will be used
        :param bool ssl_verify:
            Indicates whether the SSL certificate of the Jenkins instance should be checked upon connection.
            For Jenkins instances hosted behind HTTPS using self-signed certificates this may cause connection
            errors when enabled. Defaults to disabled (False)
        :returns:
            Jenkins object, pre-configured with the appropriate credentials and connection parameters for the given URL.
        :rtype: :class:`.Jenkins`
        """
        # If no explicit credentials provided, load credentials from any config files
        if credentials is None:
            config = JenkinsConfigParser()
            config.read(JenkinsConfigParser.get_default_configfiles())
            credentials = config.get_credentials(url)

        http_io = DataRequester(url, ssl_verify)
        http_io.credentials = credentials
        retval = Jenkins(http_io)
        return retval

    @property
    def connected(self):
        """Checks to make sure the connection to the Jenkins REST API was successful

        :returns: True if connected, false if not
        :rtype: :class:`bool`
        """
        try:
            version = self.version
        except RequestException as err:
            self._log.error("Jenkins connection failed: %s.", err)
            return False

        if version is None or version == "" or version == "Unknown":
            self._log.error("Invalid Jenkins version detected: '%s'", version)
            return False
        return True

    @property
    def version(self):
        """Gets the version of Jenkins pointed to by this object

        :return: Version number of the currently running Jenkins instance
        :rtype: :class:`str`
        """
        headers = self._controller.get_headers('/api/python')

        if 'x-jenkins' not in headers:
            return "Unknown"
        else:
            return headers['x-jenkins']

    @property
    def is_shutting_down(self):
        """checks to see whether the Jenkins master is in the process of shutting down.

        :returns:
            If the Jenkins master is preparing to shutdown
            (ie: in quiet down state), return True, otherwise returns False.
        :rtype: :class:`bool`
        """
        data = self._controller.get_api_data()

        return data['quietingDown']

    @property
    def nodes(self):
        """gets the list of nodes (aka: agents) managed by this Jenkins master

        :returns: list of 0 or more Node objects managed by this Jenkins master
        :rtype: :class:`list` of :class:`~.node.Node` objects
        """
        tmp_data_io = self._controller.clone(self._controller.url.rstrip("/") + "/computer")
        data = tmp_data_io.get_api_data()

        nodes = data['computer']
        retval = []
        for cur_node in nodes:
            if cur_node['displayName'] == 'master':
                node_url = self._controller.url.rstrip("/") + '/computer/(master)'
            else:
                node_url = self._controller.url.rstrip("/") + '/computer/' + cur_node['displayName']

            node_data_io = self._controller.clone(node_url)
            retval.append(Node(node_data_io))

        return retval

    @property
    def default_view(self):
        """returns a reference to the primary / default Jenkins view

        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view.

        :returns: object that manages the default Jenkins view
        :rtype: :class:`~.view.View`
        """
        data = self._controller.get_api_data()

        default_view = data['primaryView']
        new_io_obj = self._controller.clone(default_view['url'].rstrip("/") + "/view/" + default_view['name'])
        return View.create(new_io_obj, self)

    @property
    def views(self):
        """Gets a list of all views directly managed by the Jenkins dashboard

        To retrieve all views managed by this Jenkins instance, including recursing into
        views that support sub-views, see the :py:meth:`.all_views` property

        :returns: list of one or more views defined on this Jenkins instance.
        :rtype: :class:`list` of :class:`~.view.View` objects
        """
        data = self._controller.get_api_data()

        raw_views = data['views']
        retval = []

        for cur_view in raw_views:
            # The default view will not have a valid view URL
            # so we need to look for this and generate a corrected one
            turl = cur_view['url']
            if turl.find('view') == -1:
                turl = turl.rstrip("/") + "/view/" + cur_view['name']

            new_io_obj = self._controller.clone(turl)
            tview = View.create(new_io_obj, self)
            retval.append(tview)

        return retval

    @property
    def view_names(self):
        """Gets a list of the names of the views managed by this Jenkins instance

        :rtype: :class:`list` of :class:`~.view.View` objects
        """
        data = self._controller.get_api_data()

        raw_views = data['views']
        retval = []

        for cur_view in raw_views:
            retval.append(cur_view['name'])

        return retval

    def prepare_shutdown(self):
        """Sends a shutdown signal to the Jenkins master preventing new builds from executing

        Analogous to the "Prepare for Shutdown" link on the Manage Jenkins configuration page

        You can cancel a previous requested shutdown using the
        :py:meth:`.cancel_shutdown` method
        """
        self._controller.post('/quietDown')

    def cancel_shutdown(self):
        """Cancels a previous scheduled shutdown sequence

        Cancels a shutdown operation initiated by the
        :py:meth:`.prepare_shutdown` method
        """
        self._controller.post('/cancelQuietDown')

    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job

        .. seealso: :py:meth:`.get_job`

        :param str job_name: the name of the job to search for
        :returns:
            If a job with the specified name can be found, and object to manage the job will be returned, otherwise None
        :rtype: :class:`~.job.Job`
        """
        data = self._controller.get_api_data()
        tjobs = data['jobs']

        for tjob in tjobs:
            if tjob['name'] == job_name:
                new_io_obj = self._controller.clone(tjob['url'])
                return Job.create(new_io_obj, self)

        return None

    @property
    def all_job_names(self):
        """Gets list of all jobs found on this server"""
        retval = []

        data = self._controller.get_api_data()
        tjobs = data['jobs']

        for tjob in tjobs:
            retval.append(tjob['name'])

        return retval

    def find_view(self, view_name):
        """Searches views directly managed by this Jenkins instance for a specific view

        .. seealso: :py:meth:`.get_view`

        :param str view_name: the name of the view to search for
        :returns:
            If a view with the specified name can be found, an object to manage the view will be returned,
            otherwise None
        :rtype: :class:`~.view.View`
        """
        data = self._controller.get_api_data()

        raw_views = data['views']

        for cur_view in raw_views:
            if cur_view['name'] == view_name:
                turl = cur_view['url']
                if turl.find('view') == -1:
                    turl = turl.rstrip("/") + "/view/" + cur_view['name']

                new_io_obj = self._controller.clone(turl)
                return View.create(new_io_obj, self)

        return None

    def create_view(self, view_name, view_type):
        """Creates a new view on the Jenkins dashboard

        :param str view_name:
            the name for this new view
            This name should be unique, different from any other views
            currently managed by the Jenkins instance
        :param str view_type:
            type of view to create
            must match one or more of the available view types supported
            by this Jenkins instance. See :py:meth:`.view_types`
            for a list of supported view types.
        :returns: An object to manage the newly created view
        :rtype: :class:`~.view.View`
        """
        view_type = view_type.replace("__", "_")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }

        args = {}
        args['data'] = data
        args['headers'] = headers

        self._controller.post('/createView', args)

        retval = self.find_view(view_name)
        assert retval is not None
        return retval

    def create_job(self, job_name, job_type):
        """Creates a new job on this Jenkins instance

        :param str job_name:
            The name for the job to be created.
            expected to be universally unique on this instance of Jenkins
        :param str job_type:
            descriptive type for the base configuration of this new job
            for a list of currently supported job types see :meth:`.job_types`
        """
        params = {'name': job_name}
        headers = {'Content-Type': 'text/xml'}

        args = {}
        args['params'] = params
        args['headers'] = headers
        args['data'] = Job.template_config_xml(job_type)

        self._controller.post("createItem", args)

        temp_data_io = self._controller.clone(self._controller.url.rstrip("/") + "/job/" + job_name)
        new_job = Job.create(temp_data_io, self)

        # Sanity check - make sure the job actually exists by checking its name
        assert new_job.name == job_name

        #disable the newly created job so it doesn't accidentally start running
        new_job.disable()

        return new_job

    @property
    def job_types(self):
        """
        :returns: a list of Jenkins job types currently supported by this instance of PyJen
                 Elements from this list may be used when creating new jobs on this Jenkins instance,
                 so long as the accompanying job type is supported by the live Jenkins server
        :rtype: :class:`list` of :class:`str`
        """
        return Job.supported_types()

    @property
    def view_types(self):
        """
        :returns: a list of Jenkins view types currently supported by this instance of PyJen
                  Elements from this list may be used when creating new views on this Jenkins instance,
                  so long as the accompanying view type is supported by the live Jenkins server
        :rtype: :class:`list` of :class:`str`
        """
        return View.supported_types()

    def _clone_job(self, source_job_name, new_job_name):
        """Makes a copy of this job on the dashboard with a new name

        :param str source_job_name:
            The name of the existing Jenkins job which is to have it's configuration cloned to create a new job.
            A job of this name must exist on this Jenkins instance.
        :param str new_job_name:
            the name of the newly created job whose settings will
            be an exact copy of the source job. There must be no existing
            jobs on the Jenkins dashboard with this same name.
        """
        params = {'name': new_job_name,
                  'mode': 'copy',
                  'from': source_job_name}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        args = {}
        args['params'] = params
        args['data'] = ''
        args['headers'] = headers

        self._controller.post("createItem", args)

        temp_data_io = self._controller.clone(self._controller.url.rstrip("/") + "/job/" + new_job_name)
        new_job = Job._create(temp_data_io, self, new_job_name)

        # disable the newly created job so it doesn't accidentally start running
        new_job.disable()

    def get_view(self, url):
        """Establishes a connection to a View based on an absolute URL

        This method may be a bit less convenient to use in certain situations but it
        has better performance than :py:meth:`.find_view`

        .. seealso: :py:meth:`.find_view`

        :param str url: absolute URL of the view to load
        :return: an instance of the appropriate View subclass for the given view
        :rtype: :class:`~.view.View`
        """
        new_io_obj = self._controller.clone(url)
        return View.create(new_io_obj, self)

    def get_job(self, url):
        """Establishes a connection to a Job based on an absolute URL

        This method may be a bit less convenient to use in certain situations but it
        has better performance than :py:meth:`.find_job`

        .. seealso: :py:meth:`.find_job`

        :param str url: absolute URL of the job to load
        :return: an instance of the appropriate Job subclass for the given job
        :rtype: :class:`~.job.Job`
        """
        new_io_obj = self._controller.clone(url)
        return Job(new_io_obj, self)

    def get_user(self, url):
        """Establishes a connection to a Jenkins User based on an absolute URL

        This method may be a bit less convenient to use in certain situations but it
        has better performance than :py:meth:`.find_user`

        .. seealso: :py:meth:`.find_user`

        :param str url: absolute URL of the user to load
        :return: A user object allowing interaction with the given user's settings and information
        :rtype: :class:`~.user.User`
        """
        new_io_obj = self._controller.clone(url)
        return User(new_io_obj)

    def find_user(self, username):
        """Locates a user with the given username on this Jenkins instance

        :param str username: name of user to locate
        :returns: reference to Jenkins object that manages this users information.
        :rtype: :class:`~.user.User` or None if user not found
        """
        new_url = self._controller.url + "/user/" + username
        new_io_obj = self._controller.clone(new_url)
        try:
            retval = User(new_io_obj)
            assert retval.user_id == username
            return retval
        except RequestException:
            return None

    def get_node(self, url):
        """Loads data for a Jenkins build agent based on an absolute URL

        This method may be a bit less convenient to use in certain situations but it
        has better performance than :py:meth:`.find_node`

        .. seealso: :py:meth:`.find_node`

        :param str url: absolute URL of the node data to load
        :return: A node object allowing interaction with the given node's settings and information
        :rtype: :class:`~.node.Node`
        """
        new_io_obj = self._controller.clone(url)
        return Node(new_io_obj)

    def find_node(self, nodename):
        """Locates a Jenkins build agent with the given name on this Jenkins instance

        :param str nodename: name of node to locate
        :returns: reference to Jenkins object that manages this node's information.
        :rtype: :class:`~.node.Node` or None if node not found
        """
        new_url = self._controller.url + "/computer/" + nodename
        new_io_obj = self._controller.clone(new_url)
        try:
            retval = Node(new_io_obj)
            assert retval.name == nodename
            return retval
        except RequestException:
            return None

    @property
    def plugin_manager(self):
        """Gets object which manages the plugins installed on the current Jenkins instance

        :returns: reference to Jenkins object that manages plugins on this instance
        :rtype: :class:`~.plugin_manager.PluginManager`
        """
        new_url = self._controller.url + '/pluginManager'
        new_io_obj = self._controller.clone(new_url)
        retval = PluginManager(new_io_obj)
        return retval

    def enable_cache(self):
        """Enables caching of Jenkins API data

        WARNING: This functionality is in early prototype stage and should not be used in production environments"""
        self._controller.enable_cache()

    def disable_cache(self):
        """Disables caching of Jenkins API data

        WARNING: This functionality is in early prototype stage and should not be used in production environments"""
        self._controller.disable_cache()

    def flush_cache(self):
        """Flushes any pending writes to the remote Jenkins server

        WARNING: This method interacts with a new, crude prototype caching
        system being tested and should not be used in production
        """
        self._controller.flush()

    def reset_cache(self):
        """Resets all cached data

        WARNING: Any unwritten changes to the cache will be lost if not
        flushed previously using the flush_cache() method

        WARNING: This method interacts with a new, crude prototype caching
        system being tested and should not be used in production
        """
        self._controller.clear()

    def show_debug_info(self):
        """Streams data related to the caching subsystem to the package logger for debugging purposes"""
        self._controller.show_debug_info()

if __name__ == '__main__':  # pragma: no cover
    pass
