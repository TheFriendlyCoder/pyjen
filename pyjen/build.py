from pyjen.utils.data_requester import data_requester
from pyjen.changeset import changeset
from datetime import datetime
from pyjen.exceptions import InvalidJenkinsURLError

class build(object):
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
        
        :param str url: Full URL of the Jenkins instance to connect to. Must be a valid job on a valid Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and password for authenticating to the URL
            If no credentials can be found elsewhere, anonymous access will be chosen
        :returns: :py:mod:`pyjen.job` object, pre-configured with the appropriate credentials
            and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.job`
        """
        if credentials != None:
            username = credentials[0]
            password = credentials[1]
        else:
            username = ""
            password = ""
        
        http_io = data_requester(url, username, password)
        retval = build(http_io)
        
        # Sanity check: make sure we can successfully parse the view's name from the IO controller to make sure
        # we have a valid configuration
        try:
            number = retval.get_build_number()
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Build. Please check configuration.", http_io) 
        if number == None or number <= 0:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Build. Please check configuration.", http_io) 
    
        return retval
        
    def get_build_number(self):
        """Gets the numeric build number for this build
        
        :returns: This is the unique numeric identifier, typically a
            sequential integer that is incremented with each build.
        :rtype: :func:`int`
        """
        
        data = self.__data_io.get_api_data()
        
        return data['number']
    
    def get_build_time(self):
        """Gets the time stamp of when this build was executed
        
        :returns: the date and time at which this build was executed
        :rtype: :class:`datetime.datetime`
            
        """
        
        data = self.__data_io.get_api_data()
        
        time_in_seconds = data['timestamp'] * 0.001
        
        return datetime.fromtimestamp(time_in_seconds)
    
    def is_building(self):
        """Checks to see whether this build is currently executing
        
        :returns: true if the build is executing otherwise false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()
        
        return data['building']
    
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

    def get_console_output(self):
        """Gets the raw console output for this build as plain text
        :rtype: :func:`str`
        """
        return self.__data_io.get_text("/consoleText")
    
if __name__ == "__main__":
    pass