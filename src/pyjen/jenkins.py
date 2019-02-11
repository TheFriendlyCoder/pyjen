"""Primitives for interacting with the main Jenkins dashboard"""
import logging
from requests.exceptions import RequestException
from pyjen.view import View
from pyjen.node import Node
from pyjen.job import Job
from pyjen.user import User
from pyjen.plugin_manager import PluginManager
from pyjen.utils.user_params import JenkinsConfigParser
from pyjen.utils.jenkins_api import JenkinsAPI
from pyjen.exceptions import PluginNotSupportedError
from pyjen.utils.configxml import ConfigXML


class Jenkins(JenkinsAPI):
    """Python wrapper managing the Jenkins primary dashboard

    Generally you should use this class as the primary entry point to the PyJen APIs. Finer grained control of each
    aspect of the Jenkins dashboard is then provided by the objects exposed by this class including:

    * :class:`~.view.View` - abstraction for a view on the dashboard, allowing
      jobs to be filtered based on different criteria like job name.
    * :class:`~.job.Job` - abstraction for a Jenkins job, allowing manipulation
      of job settings and controlling builds of those jobs
    * :class:`~.build.Build` - abstraction for an instance of a build of a particular job

    **Example:** finding a job ::

        j = pyjen.Jenkins('http://localhost:8080')
        job = j.find_job('My Job')
        if job is None:
            print ('no job by that name found')
        else:
            print ('job ' + job.name + ' found')

    **Example:** find the build number of the last good build of the first job on the default view ::

        j = pyjen.Jenkins('http://localhost:8080/')
        v = j.get_default_view()
        jobs = v.get_jobs()
        lgb = jobs[0].last_good_build
        print ('last good build of the first job in the default view is ' + lgb.get_build_number())

    :param str url: Full HTTP URL to the main Jenkins dashboard
    :param tuple credentials:
        Optional 2-tuple containing the username and password / api key to authenticate with
        If not provided, credentials will be loaded from any PyJen config files detected on the system.
        If no config files can be found, anonymous access will be assumed
    :param bool ssl_verify:
        flag indicating whether SSL certificates should be verified or not on this connection
        Enabling this flag on servers running Jenkins behind an HTTPS connect with self-signed SSL certificates
        will result in connection errors
    """

    def __init__(self, url, credentials=None, ssl_verify=False):
        super(Jenkins, self).__init__(url)
        self._log = logging.getLogger(__name__)

        # If no explicit credentials provided, load credentials from any config files
        if credentials is None:
            config = JenkinsConfigParser()
            config.read(JenkinsConfigParser.get_default_configfiles())
            JenkinsAPI.creds = config.get_credentials(url)
        else:
            JenkinsAPI.creds = credentials

        JenkinsAPI.ssl_verify_enabled = ssl_verify
        JenkinsAPI.jenkins_root_url = self.url

        #TODO: Consider adding a "debugging" flag that enables extra error checking on the API, then
        #       add in extra checks for data types, URLs and such throughout.

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
        return self.jenkins_version

    @property
    def is_shutting_down(self):
        """checks to see whether the Jenkins master is in the process of shutting down.

        :returns:
            If the Jenkins master is preparing to shutdown
            (ie: in quiet down state), return True, otherwise returns False.
        :rtype: :class:`bool`
        """
        data = self.get_api_data()

        return data['quietingDown']

    @property
    def nodes(self):
        """gets the list of nodes (aka: agents) managed by this Jenkins master

        :returns: list of 0 or more Node objects managed by this Jenkins master
        :rtype: :class:`list` of :class:`~.node.Node` objects
        """
        data = self.get_api_data(target_url=self.url + "computer/")
        nodes = data['computer']
        retval = []
        for cur_node in nodes:
            if cur_node['displayName'] == 'master':
                node_url = self.url + 'computer/(master)'
            else:
                node_url = self.url + 'computer/' + cur_node['displayName']

            retval.append(Node(node_url))

        return retval

    @property
    def default_view(self):
        """returns a reference to the primary / default Jenkins view

        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view.

        :returns: object that manages the default Jenkins view
        :rtype: :class:`~.view.View`
        """
        data = self.get_api_data()

        default_view = data['primaryView']

        # TODO: Add 'verify' method to job and view classes so callers can choose if they want
        #       to ensure their returned objects actually exist (ie; have a valid rest api endpoint)
        return View(default_view['url'] + "view/" + default_view['name'])

    @property
    def views(self):
        """Gets a list of all views directly managed by the Jenkins dashboard

        To retrieve all views managed by this Jenkins instance, including recursing into
        views that support sub-views, see the :py:meth:`.all_views` property

        :returns: list of one or more views defined on this Jenkins instance.
        :rtype: :class:`list` of :class:`~.view.View` objects
        """
        data = self.get_api_data()

        raw_views = data['views']
        retval = []

        for cur_view in raw_views:
            turl = cur_view['url']

            # The default view will not have a valid view URL
            # so we need to look for this and generate a corrected one
            if '/view/' not in turl:
                turl = turl + "view/" + cur_view['name']

            tview = View(turl)
            retval.append(tview)

        return retval

    def prepare_shutdown(self):
        """Sends a shutdown signal to the Jenkins master preventing new builds from executing

        Analogous to the "Prepare for Shutdown" link on the Manage Jenkins configuration page

        You can cancel a previous requested shutdown using the
        :py:meth:`.cancel_shutdown` method
        """
        self.post(self.url + 'quietDown')

    def cancel_shutdown(self):
        """Cancels a previous scheduled shutdown sequence

        Cancels a shutdown operation initiated by the
        :py:meth:`.prepare_shutdown` method
        """
        self.post(self.url + 'cancelQuietDown')

    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job

        .. seealso: :py:meth:`.get_job`

        :param str job_name: the name of the job to search for
        :returns:
            If a job with the specified name can be found, and object to manage the job will be returned, otherwise None
        :rtype: :class:`~.job.Job`
        """
        data = self.get_api_data()
        tjobs = data['jobs']

        for tjob in tjobs:
            if tjob['name'] == job_name:
                return Job(tjob['url'])

        return None

    def find_view(self, view_name):
        """Searches views directly managed by this Jenkins instance for a specific view

        .. seealso: :py:meth:`.get_view`

        :param str view_name: the name of the view to search for
        :returns:
            If a view with the specified name can be found, an object to manage the view will be returned,
            otherwise None
        :rtype: :class:`~.view.View`
        """
        data = self.get_api_data()

        raw_views = data['views']

        for cur_view in raw_views:
            if cur_view['name'] == view_name:
                turl = cur_view['url']
                # TODO: Consider encapsulating the 'default view' URL handling in the View() constructor
                if 'view' not in turl:
                    turl += "view/" + cur_view['name']

                return View(turl)

        return None

    def create_view(self, view_name, view_type):
        """Creates a new view on the Jenkins dashboard

        :param str view_name:
            the name for this new view
            This name should be unique, different from any other views currently managed by the Jenkins instance
        :param str view_type:
            type of view to create
            must match one or more of the available view types supported by this Jenkins instance.
            See :py:meth:`~.view.View.supported_types` for a list of supported view types.
        :returns: An object to manage the newly created view
        :rtype: :class:`~.view.View`
        """
        self._create_view(view_name, view_type)

        retval = self.find_view(view_name)
        assert retval is not None
        return retval

    @staticmethod
    def get_plugin_template(plugin_type):
        """Helper method that retrieves a default XML template for constructing an object from a specific plugin

        :param str plugin_type: name of a specific plugin to load the template configuration for"""
        plugin = ConfigXML.find_plugin(plugin_type)
        if plugin is not None:
            return plugin.template_config_xml()

        raise PluginNotSupportedError("Plugin {0} not found".format(plugin_type), plugin_type)

    def find_user(self, username):
        """Locates a user with the given username on this Jenkins instance

        :param str username: name of user to locate
        :returns: reference to Jenkins object that manages this users information.
        :rtype: :class:`~.user.User` or None if user not found
        """
        # TODO: Rework 'users' property to cache the user name for all users in one query, so we can rework
        #       this implementation to simply call self.users then iterate through them all to find the one
        #       we're looking for. Then we don't have to guess the URL.
        new_url = self.url + "user/" + username
        try:
            retval = User(new_url)
            assert retval.user_id == username
            return retval
        except RequestException:
            return None

    def find_node(self, nodename):
        """Locates a Jenkins build agent with the given name on this Jenkins instance

        :param str nodename: name of node to locate
        :returns: reference to Jenkins object that manages this node's information.
        :rtype: :class:`~.node.Node` or None if node not found
        """
        if nodename == "master":
            temp_nodename = "(master)"
        else:
            temp_nodename = nodename

        # TODO: Rework 'nodes' property to cache the node name for all nodes in one query, so we can rework
        #       this implementation to simply call self.nodess then iterate through them all to find the one
        #       we're looking for. Then we don't have to guess the URL.

        new_url = self.url + "computer/" + temp_nodename
        try:
            retval = Node(new_url)
            assert retval.name == nodename
            return retval
        except RequestException:
            return None

    @property
    def plugin_manager(self):  # pragma: no cover
        """Gets object which manages the plugins installed on the current Jenkins instance

        :returns: reference to Jenkins object that manages plugins on this instance
        :rtype: :class:`~.plugin_manager.PluginManager`
        """
        return PluginManager(self.url + 'pluginManager')


if __name__ == '__main__':  # pragma: no cover
    pass
