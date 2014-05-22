import sys
import os
from pyjen.exceptions import InvalidUserParamsError

if sys.version_info.major < 3:
    import ConfigParser as configparser
else:
    import configparser
    
class UserParameters(object):
    """Interface that manages all user-configurable properties dictating the behavior of the rest of the PyJen API."""

    def __init__ (self, config_file=None):
        """Constructor
        
        ::
        
            Config File Format
            ==================
            Required sections
            ------------------
            [jenkins_config]
            jenkins_url=http://jenkins_server_url
            
            Optional Sections
            -------------------
            [credentials]
            username=MyUserName
            password=MyPassword
            
        For more details on the general format of the config file see these links:
            https://wiki.python.org/moin/ConfigParserExamples
            https://docs.python.org/2/library/configparser.html
        
        :param str config_file:
            optional configuration file containing definitions for all required attributes
            for the PyJen api
            If not defined, a set of default values will be generated
        """
        if config_file == None:
            self.__load_defaults()
            return
        
        if not os.path.exists(config_file):
            raise IOError("User configuration file " + config_file + " not found.")
        
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        if not parser.has_section("jenkins_config"):
            raise InvalidUserParamsError("Missing section: jenkins_config", config_file)
        
        jenkins_params = {item[0]:item[1] for item in parser.items("jenkins_config")}
        
        if not "url" in jenkins_params.keys():
            raise InvalidUserParamsError("Missing 'url' property in user configuration file.", config_file)    
            
        self.__jenkins_url = jenkins_params['url']
        
        #Make sure we're always have a trailing slash character to simplify later processes
        if not self.__jenkins_url.endswith('/'):
            self.__jenkins_url += '/'
        
        if parser.has_section("credentials"):
            credentials_params = {item[0]:item[1] for item in parser.items("credentials")}
            if not "username" in credentials_params.keys():
                raise InvalidUserParamsError("Missing 'username' property from 'credentials' section of user configuration file.", config_file)
            if not "password" in credentials_params.keys():
                raise InvalidUserParamsError("Missing 'password' property from 'credentials' section of user configuration file.", config_file)
            
            self.__username = credentials_params['username']
            self.__password = credentials_params['password']
            self.__anonymous = False
        else:
            self.__anonymous = True
    
    def __load_defaults(self):
        """Loads a set of default values for all properties"""
        self.__anonymous = True
        self.__username = ""
        self.__password = ""
        self.__jenkins_url = "http://localhost:8080"
        
    def set_credentials (self, username, password):
        """Overloads default login credentials
        
        :param str username:
            name of user to be authenticated as
            If set to an empty string or None, credentials
            will be configured for anonymous access
        :param str password:
            Jenkins password for the specified users
        """
        if username == None or username == "":
            self.__username = ""
            self.__password = ""
            self.__anonymous = True
        else:    
            self.__username = username
            self.__password = password
            self.__anonymous = False
            
    def set_jenkins_url(self, new_url):
        """Changes the Jenkins root URL
        
        :param str new_url: url to a new Jenkins instance
        """
        
        self.__jenkins_url = new_url

    
    @property
    def jenkins_url(self):
        """Gets the root URL for the current Jenkins instance
        
        :returns: root URL for the current Jenkins instance
        :rtype: :func:`str`
        """
        return self.__jenkins_url
    
    @property
    def username(self):
        """Gets the name of the user to authenticate with on the Jenkins instance
        
        May be empty if anonymous authenticate enabled. See :py:func:`anonymous_logon` for details.
    
        :rtype: :func:`str`
        """ 
        return self.__username
    
    @property
    def password(self):
        """Gets the password to authenticate the given user against the Jenkins instance
        
        May be empty if anonymous authentication is enabled. See :py:func:`anonymous_logon` for details.
    
        :rtype: :func:`str`
        """
        return self.__password
    
    @property
    def credentials(self):
        """Convenience method that returns the authentication credentials as a tuple
        
        Most authenticated methods that take a user name and password as input
        require that those values be provided in a tuple, with the first element
        being the username and the second element the password. This method simply
        wraps the individual credentials provided by the :py:func:`username` and :py:func:`password`
        properties in a tuple.
        
        :returns:
            2-element tuple, containing the username and password for authenticated
            connections
            e.g. (username, password)
            
            NOTE: if this configuration does not support authentication 
            (e.g.: anonymous_logon == True) this method will simply
            return None.
        :rtype: :func:`tuple`
        """
        if (self.anonymous_logon):
            return None
        
        return (self.username, self.password)
    
    @property
    def anonymous_logon(self):
        """Checks to see whether anonymous authentication should be used when connecting to Jenkins
        
        NOTE:
        If anonymous authentication is being used the values of the :py:func:`username` and
        :py:func:`password` properties will be unreliable.
        
        :returns:
            True if anonymous logon is to be used
            False if authenticated logon should be used
        :rtype: :func:`bool`
        """
        return self.__anonymous
    



#---------------------------------- HELPER FUNCTIONS ------------------------------------
def _FindDefaultConfigFile():
    """Internal helper method used to search several predefined locations for a pyjen config file
    
    :returns:
        Path to the appropriate default configuration file, if found
        Otherwise returns None
    
    :rtype: :func:`str`
    """
    
    #static default file name to look for
    default_config_filename = ".pyjen"
    
    #Step 1: Look in the current folder
    f = os.path.join(os.getcwd(), default_config_filename)
    if os.path.exists(f) and os.path.isfile(f):
        return f
    
    #Step 2: Look in the users home folder
    f = os.path.join(os.path.expanduser("~"), default_config_filename)
    if os.path.exists(f) and os.path.isfile(f):
        return f
    
    #Finally, if no default config file can be found, return None
    return None


_GlobalParams = None
def GlobalParams():
    """Singleton-like function exposing a global set of user parameters shareable across the entire PyJen API
    
    :returns: Object that manages user defined configuration parameters to PyJen API
    
    :rtype: :py:mod:`pyjen.user_params`
    """
    global _GlobalParams
    if _GlobalParams == None:
        _GlobalParams = UserParameters(_FindDefaultConfigFile())
    return _GlobalParams

if __name__ == "__main__":
    pass