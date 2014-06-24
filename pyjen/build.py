from pyjen.utils.data_requester import data_requester
from pyjen.changeset import changeset
from datetime import datetime

class build(object):
    """Class that encapsulates all jenkins related 'build' information
    
    Builds are executions of jobs and thus instances of this class are
    typically generated from the :py:mod:`pyjen.job` class.
    """
    
    
    def __init__ (self, url, http_io_class=data_requester):
        """constructor
        
        :param str url: URL of the build to be managed. This may be a full URL, starting with
            the root Jenkins URL, or a partial URL relative to the Jenkins root
            
            Examples: 
                * 'http://jenkins/jobs/job1/123'
                * 'jobs/job2'
                
        :param http_io_class:
            class capable of handling HTTP IO requests between
            this class and the Jenkins REST API
            If not explicitly defined a standard IO class will be used 
        """
        self.__requester = http_io_class(url)        
        data = self.__requester.get_api_data()      
        self._buildNumber = data['number']
        
        time_in_seconds = data['timestamp'] * 0.001        
        self._buildTime = datetime.fromtimestamp(time_in_seconds)
                
    @property
    def buildNumber(self):
        return self._buildNumber
    
    @property
    def buildTime(self):
        return self._buildTime   
    
    def get_url(self):
        """Returns the root URL for the REST API that manages this build
        
        :returns: the root URL for the REST API that controls this build
        :rtype: :func:`str`
        """
        return self.__requester.url
        
    def get_url(self):
        """Returns the root URL for the REST API that manages this build
        
        :returns: the root URL for the REST API that controls this build
        :rtype: :func:`str`
        """
        return self.__requester.url
    
    def get_build_number(self):
        """Gets the numeric build number for this build
        
        :returns: This is the unique numeric identifier, typically a
            sequential integer that is incremented with each build.
        :rtype: :func:`int`
        """
        
        data = self.__requester.get_api_data()
        
        return data['number']
    
    def get_culprits(self):
        """gets a list of all the culprits from the build
        
        :returns
        list of culprits        
        'fullName' - :func: `str`
            - Full name of the user
        'absoluteUrl' - :func: `str`
            - URL to the jenkins user page
        """
        
        retval = {}
        data = self.__requester.get_api_data()
        for item in data['culprits']:
            retval.update({item['fullName']:item['absoluteUrl']})
            
        return retval
        
    def get_build_time(self):
        """Gets the time stamp of when this build was executed
        
        :returns: the date and time at which this build was executed
        :rtype: :class:`datetime.datetime`
            
        """
        
        data = self.__requester.get_api_data()
        
        time_in_seconds = data['timestamp'] * 0.001
        
        return datetime.fromtimestamp(time_in_seconds)
    
    def is_building(self):
        """Checks to see whether this build is currently executing
        
        :returns: true if the build is executing otherwise false
        :rtype: :func:`bool`
        """
        data = self.__requester.get_api_data()
        
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
        data = self.__requester.get_api_data()
        
        return changeset(data['changeSet'])

    def get_console_output(self):
        """Gets the raw console output for this build as plain text
        :rtype: :func:`str`
        """
        return self.__requester.get_text("/consoleText")
    
if __name__ == "__main__":
    j = build('http://localhost:8080/job/test_job_1/1/')
    print (j.get_console_output())
