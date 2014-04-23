from pyjen.utils.data_requester import data_requester
from pyjen.changeset import changeset
from datetime import datetime

class build(object):
    """Class that encapsulates all jenkins related 'build' information
    
    Builds are executions of jobs and thus instances of this class are
    typically generated from the pyjen.job class.
    """
    
    
    def __init__ (self, url, user=None, password=None, custom_data_requester=None):
        """constructor
        
        Parameters
        ----------
        url : string
            root URL of the node being managed by this object
            Example: 'http://jenkins/job/job1/789'
        user : string
            optional user name to authenticate with Jenkins
        password : string
            optional password for the specified user
            if a user name is provided this parameter must be non-empty
        custom_data_requester : object
            object providing interface for querying and posting data
            from / to an HTTP URL. Typically used for unit testing by
            allowing mock IO objects to be injected into the class.
            If not provided the default HTTP request object will be used
        """
        if (user != None):
            assert (password != None)
        
        self.__url = url
        if custom_data_requester == None:
            self.__requester = data_requester(self.__url, user, password)
        else:
            self.__requester = custom_data_requester

    def get_url(self):
        """Returns the root URL for the REST API that manages this build
        
        Return
        ------
        string
            the root URL for the REST API that controls this build
        """
        return self.__url
    
    def get_build_number(self):
        """Gets the numeric build number for this build
        
        This is the unique numeric identifier, typically a
        sequential integer that is incremented with each build.
        """
        
        data = self.__requester.get_data("/api/python")
        
        return data['number']
    
    def get_build_time(self):
        """Gets the time stamp of when this build was executed
        
        Return
        ------
        datetime object
            the date and time at which this build was executed
        """
        
        data = self.__requester.get_data("/api/python")
        
        time_in_seconds = data['timestamp'] * 0.001
        
        return datetime.fromtimestamp(time_in_seconds)
    
    def is_building(self):
        """Checks to see whether this build is currently executing
        
        Return
        ------
        boolean
            true if the build is executing otherwise false
        """
        data = self.__requester.get_data("/api/python")
        
        return data['building']
    
    def get_changeset(self):
        """Gets changeset object associated with this build
        
        NOTE: This changeset may be empty if there were no SCM
        changes associated with this build, as may be the case
        with a forced build for example.
        
        Return
        ------
        pyjen.changeset
            Changeset object representing the set of SCM changes
            associated with / included in this build
        """
        data = self.__requester.get_data("/api/python")
        
        return changeset(data['changeSet'])

    def get_console_output(self):
        """Gets the raw console output for this build as plain text"""
        return self.__requester.get_text("/consoleText")
    
if __name__ == "__main__":
    j = build('http://localhost:8080/job/test_job/1')
    print (j.get_console_output())