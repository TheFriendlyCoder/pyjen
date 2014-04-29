from pyjen.utils.data_requester import data_requester
from pyjen.changeset import changeset
from datetime import datetime

class build(object):
    """Class that encapsulates all jenkins related 'build' information
    
    Builds are executions of jobs and thus instances of this class are
    typically generated from the pyjen.job class.
    """
    
    
    def __init__ (self, url, http_io_class=data_requester):
        """constructor
        
        Parameters
        ----------
        url : string
            URL of the build to be managed. This may be a full URL, starting with
            the root Jenkins URL, or a partial URL relative to the Jenkins root
            
            Examples: 
                * 'http://jenkins/jobs/job1/123'
                * 'jobs/job2'
                
        http_io_class : Python class object
            class capable of handling HTTP IO requests between
            this class and the Jenkins REST API
            If not explicitly defined a standard IO class will be used 
        """
        self.__requester = http_io_class(url)
        
    def get_url(self):
        """Returns the root URL for the REST API that manages this build
        
        Return
        ------
        string
            the root URL for the REST API that controls this build
        """
        return self.__requester.url
    
    def get_build_number(self):
        """Gets the numeric build number for this build
        
        This is the unique numeric identifier, typically a
        sequential integer that is incremented with each build.
        """
        
        data = self.__requester.get_api_data()
        
        return data['number']
    
    def get_build_time(self):
        """Gets the time stamp of when this build was executed
        
        Return
        ------
        datetime object
            the date and time at which this build was executed
        """
        
        data = self.__requester.get_api_data()
        
        time_in_seconds = data['timestamp'] * 0.001
        
        return datetime.fromtimestamp(time_in_seconds)
    
    def is_building(self):
        """Checks to see whether this build is currently executing
        
        Return
        ------
        boolean
            true if the build is executing otherwise false
        """
        data = self.__requester.get_api_data()
        
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
        data = self.__requester.get_api_data()
        
        return changeset(data['changeSet'])

    def get_console_output(self):
        """Gets the raw console output for this build as plain text"""
        return self.__requester.get_text("/consoleText")
    
if __name__ == "__main__":
    j = build('http://localhost:8080/job/test_job_1/1/')
    print (j.get_console_output())
