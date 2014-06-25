from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError

class user (object):
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
        
        :param str url: Full URL of the Jenkins instance to connect to. Must be a valid job on a valid Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and password for authenticating to the URL
            If no credentials can be found elsewhere, anonymous access will be chosen
        :returns: :py:mod:`pyjen.user` object, pre-configured with the appropriate credentials
            and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.user`
        """
        if credentials != None:
            username = credentials[0]
            password = credentials[1]
        else:
            username = ""
            password = ""
        
        http_io = data_requester(url, username, password)
        retval = user(http_io)
        
        # Sanity check: make sure we can successfully parse the users ID from the IO controller to make sure
        # we have a valid configuration
        try:
            user_id = retval.get_id()
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.user. Please check configuration.", http_io) 
        if user_id == None or user_id == "":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.user. Please check configuration.", http_io) 
    
        return retval
    
    def get_user_id(self):
        """Gets the unique identifier for this user
        
        :returns: unique identifier for this user
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['id']
    
    def get_full_username(self):
        """Gets the users full name, typically first and last names separated by a space
        
        :returns: this users' full name
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['fullName']
    
    def get_description(self):
        """Gets some descriptive text associated with the user
        
        :returns: some descriptive text explaining something about this user. 
            May be None if no description found 
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['description']
    
    def get_email(self):
        """Gets this users' email address as reported by Jenkins
        
        :returns: email address of this user 
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()
        return data['address']
    
if __name__ == "__main__":
    pass