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
        
        Config File Format
        ==================
        Required sections
        ------------------
        [jenkins_config]
        url=http://jenkins_server_url
        
        Optional Sections
        -------------------
        [credentials]
        username=MyUserName
        password=MyPassword
        
        
        For more details on the general format of the config file see these links:
        * https://wiki.python.org/moin/ConfigParserExamples
        * https://docs.python.org/2/library/configparser.html
        
        Parameters
        -------------
        config_file
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
            
        self.__url = jenkins_params['url']
        
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
        self.__url = "http://localhost:8080"
        
    def set_credentials (self, username, password):
        """Overloads default login credentials
        
        Parameters
        -----------
        username
            name of user to be authenticated as
        password
            Jenkins password for the specified users
        """
            
        self.__username = username
        self.__password = password
        self.__anonymous = False
        
    @property
    def url(self):
        """Gets the root URL for the current Jenkins instance"""
        return self.__url
    
    @property
    def username(self):
        """Gets the name of the user to authenticate with on the Jenkins instance
        
        May be empty if anonymous authenticate enabled. See anonymous_logon() for details.""" 
        return self.__username
    
    @property
    def password(self):
        """Gets the password to authenticate the given user against the Jenkins instance
        
        May be empty if anonymous authentication is enabled. See anonymous_logon() for details."""
        return self.__password
    
    @property
    def anonymous_logon(self):
        """Checks to see whether anonymous authentication should be used when connecting to Jenkins
        
        NOTE:
        If anonymous authentication is being used the values of the username() and
        password() properties will be unreliable.
        
        Returns
        -------
        True if anonymous logon is to be used
        False if authenticated logon should be used
        """
        return self.__anonymous
    
if __name__ == "__main__":
    pass