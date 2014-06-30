from pyjen.user_params import JenkinsConfigParser
from pyjen.exceptions import InvalidUserParamsError
import unittest
import pytest
import os
import platform

class JenkisConfigParser_tests(unittest.TestCase):
    def test_get_default_configfiles(self):
        default_config_files = JenkinsConfigParser.get_default_configfiles()
        
        # Currently we look in 2 locations for config files
        self.assertEqual(len(default_config_files), 2)
        
        # The least privileged location should be the users home folder
        self.assertTrue(default_config_files[0].startswith(os.path.join(os.path.expanduser("~"))))
        
        # the next most privileged location is the local working folder
        self.assertTrue(default_config_files[1].startswith(os.getcwd()))
        
        # In any case, each path must point to the expected config file name
        if platform.system() == "Windows":
            expected_filename = "pyjen.cfg"
        else:
            expected_filename = ".pyjen"
        for filename in default_config_files:
            self.assertTrue(filename.endswith(expected_filename))
            
    def test_get_credentials_empty_configuration(self):
        test_obj = JenkinsConfigParser()
        sample_config=""
        test_obj.read_string(sample_config)
        
        self.assertEqual(test_obj.get_credentials("http://localhost:8080"), None, 
                         "Empty config files should provide empty credentials")
        
    def test_get_credentials_anonymous(self):
        test_url = "http://localhost:8080"
        sample_config="""[http://localhost:8080]
        username=
        password=
        """
        test_obj = JenkinsConfigParser()
        test_obj.read_string(sample_config)
        
        self.assertEqual(test_obj.get_credentials(test_url), None, 
                         "Config explicitly declares empty username and password which should \
                         be reported as empty credentials")

    def test_get_credentials(self):
        test_url = "http://localhost:8080"
        expected_username = "jdoe"
        expected_password = "Password123"
        
        sample_config="""[http://localhost:8080]
        username=jdoe
        password=Password123
        """
        test_obj = JenkinsConfigParser()
        test_obj.read_string(sample_config)
        
        actual_credentials = test_obj.get_credentials(test_url)
        self.assertEqual(actual_credentials[0], expected_username)
        self.assertEqual(actual_credentials[1], expected_password)
        
    def test_empty_section(self):
        test_url = "http://localhost:8080"
        sample_config="[http://localhost:8080]"
        test_obj = JenkinsConfigParser()
        test_obj.read_string(sample_config)
        
        self.assertEqual(test_obj.get_credentials(test_url), None, 
                         "Undefined credentials should be reported as empty")
        
    def test_get_credentials_no_username(self):
        test_url = "http://localhost:8080"
        
        sample_config="""[http://localhost:8080]
        password=Password123
        """
        test_obj = JenkinsConfigParser()
        test_obj.read_string(sample_config)
        
        self.assertRaises(InvalidUserParamsError, test_obj.get_credentials, test_url)
        
    def test_get_credentials_no_password(self):
        test_url = "http://localhost:8080"
        
        sample_config="""[http://localhost:8080]
        username=jdoe
        """
        test_obj = JenkinsConfigParser()
        test_obj.read_string(sample_config)
        
        self.assertRaises(InvalidUserParamsError, test_obj.get_credentials, test_url)
        
    
if __name__ == "__main__":
    pytest.main()