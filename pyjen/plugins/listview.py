"""Primitives that operate on Jenkins views of type 'List'"""
from pyjen.view import View
from pyjen.user_params import JenkinsConfigParser
from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError

class ListView(View):
    """Class that encapsulates all Jenkins related 'view' information for views of type ListView

    Instances of this class are typically instantiated directly or indirectly through :py:meth:`pyjen.View.create`
    """
    type = "hudson.model.ListView"
    def __init__(self, data_io_controller, jenkins_master):
        """constructor

        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        """
        super(ListView, self).__init__(data_io_controller, jenkins_master)

    @staticmethod
    def easy_connect(url, credentials=None):
        """Factory method to simplify creating connections to Jenkins servers

        :param str url: Full URL of the Jenkins instance to connect to. Must be
            a valid running Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and
            password for authenticating to the URL
            If omitted, credentials will be loaded from any pyjen config files found on the system
            If no credentials can be found, anonymous access will be used
        :returns: :py:mod:`pyjen.Jenkins` object, pre-configured with the
            appropriate credentials and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.Jenkins`
        """
        # Default to anonymous access
        username = None
        password = None

        # If not explicit credentials provided, load credentials from any config files
        if not credentials:
            config = JenkinsConfigParser()
            config.read(JenkinsConfigParser.get_default_configfiles())
            credentials = config.get_credentials(url)

        # If explicit credentials have been found, use them rather than use anonymous access
        if credentials:
            username = credentials[0]
            password = credentials[1]


        http_io = data_requester(url, username, password)
        retval = ListView(http_io, None)

        # Sanity check: make sure we can successfully parse the view's name from the IO controller
        # to make sure we have a valid configuration
        try:
            name = retval.name
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.View. \
                Please check configuration.", http_io)
        if name == None or name == "":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.View. \
                Please check configuration.", http_io)

        return retval


if __name__ == "__main__":  # pragma: no cover
    pass
