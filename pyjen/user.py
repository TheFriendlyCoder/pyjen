"""Primitives for interacting with Jenkins jobs"""
from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError
from pyjen.user_params import JenkinsConfigParser

class User (object):
    """Interface to all primitives associated with a Jenkins user"""
    
    def __init__ (self, data_io_controller):
        """Constructor
        
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
        retval = User(http_io)
        
        # Sanity check: make sure we can successfully parse the users ID from the IO controller 
        # to make sure we have a valid configuration
        try:
            user_id = retval.user_id
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.user. \
                Please check configuration.", http_io) 
        if user_id == None or user_id == "":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.user. \
                Please check configuration.", http_io) 
    
        return retval
    
    @property
    def user_id(self):
        """Gets the unique identifier for this user
        
        :returns: unique identifier for this user
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['id']
    
    @property
    def full_name(self):
        """Gets the users full name, typically first and last names separated by a space
        
        :returns: this users' full name
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['fullName']
    
    @property
    def description(self):
        """Gets some descriptive text associated with the user
        
        :returns: some descriptive text explaining something about this user. 
            May be None if no description found 
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['description']
    
    @property
    def email(self):
        """Gets this users' email address as reported by Jenkins
        
        :returns: email address of this user 
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        for prop in data['property']:
            if 'address' in prop:
                return prop['address']
        
        return None
    
if __name__ == "__main__":
    pass
