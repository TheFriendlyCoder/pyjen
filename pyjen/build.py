"""Primitives for interacting with Jenkins builds"""

from pyjen.utils.data_requester import data_requester
from pyjen.changeset import changeset
from pyjen.user import User
from datetime import datetime
from pyjen.exceptions import InvalidJenkinsURLError
from pyjen.user_params import JenkinsConfigParser

class Build(object):
    """Class that encapsulates all jenkins related 'build' information

    Builds are executions of jobs and thus instances of this class are
    typically generated from the :py:mod:`pyjen.job` class.
    """


    def __init__ (self, data_io_controller):
        """constructor

        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        """
        self.__data_io = data_io_controller

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
        retval = Build(http_io)

        # Sanity check: make sure we can successfully parse the view's name from
        # the IO controller to make sure we have a valid configuration
        try:
            number = retval.build_number
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters \
                provided to PyJen.Build. Please check configuration.", http_io)
        if number == None or number <= 0:
            raise InvalidJenkinsURLError("Invalid connection parameters \
                provided to PyJen.Build. Please check configuration.", http_io)

        return retval

    @property
    def build_number(self):
        """Gets the numeric build number for this build

        :returns: This is the unique numeric identifier, typically a
            sequential integer that is incremented with each build.
        :rtype: :func:`int`
        """

        data = self.__data_io.get_api_data()

        return data['number']

    @property
    def build_time(self):
        """Gets the time stamp of when this build was executed

        :returns: the date and time at which this build was executed
        :rtype: :class:`datetime.datetime`

        """

        data = self.__data_io.get_api_data()

        time_in_seconds = data['timestamp'] * 0.001

        return datetime.fromtimestamp(time_in_seconds)

    @property
    def is_building(self):
        """Checks to see whether this build is currently executing

        :returns: true if the build is executing otherwise false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()

        return data['building']

    @property
    def console_output(self):
        """Gets the raw console output for this build as plain text

        :returns: Raw console output from this build, in plain text format
        :rtype: :func:`str`
        """
        return self.__data_io.get_text("/consoleText")

    @property
    def culprits(self):
        """Gets a list of potential breakers of a build

        :returns: List of 0 or more Jenkins users whom committed changes
            included in this build.
        :rtype: :func:`list` of :py:mod:`pyjen.User` objects
        """

        data = self.__data_io.get_api_data()
        retval = []
        for culprit in data['culprits']:
            temp_data_io = self.__data_io.clone(culprit['absoluteUrl'])
            temp_user = User(temp_data_io)
            retval.append(temp_user)

        return retval
    
    def get_changeset(self):
        """Gets changeset object associated with this build

        NOTE: This changeset may be empty if there were no SCM
        changes associated with this build, as may be the case
        with a forced build for example.

        :returns:
            Changeset object representing the set of SCM changes
            associated with / included in this build
        :rtype: :py:mod:`pyjen.changeset`
        """
        data = self.__data_io.get_api_data()

        return changeset(data['changeSet'])

    

if __name__ == "__main__":
    pass
