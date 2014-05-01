from pyjen.user_params import UserParameters
from pyjen.exceptions import InvalidUserParamsError

import test_utils
import unittest

class UserParameters_tests(unittest.TestCase):
    def test_simple_config(self):
        src_file = test_utils.get_test_data_file("simple_config.cfg")
        obj = UserParameters(src_file)
        self.assertEquals(obj.jenkins_url, "http://MyServer/jenkins/", "Parsed URL not as expected")
        self.assertTrue(obj.anonymous_logon,  "Should have anonymous logon enabled")
        
    def test_complete_config(self):
        src_file = test_utils.get_test_data_file("complete_config.cfg")
        obj = UserParameters(src_file)
        self.assertEquals("http://MyServer/jenkins/", obj.jenkins_url, "Parsed URL not as expected")
        self.assertFalse(obj.anonymous_logon,  "Should have anonymous logon disbled")
        self.assertEquals("MyUser", obj.username, "Authenticated user name not as expected")
        self.assertEquals("MyPassword!", obj.password, "Authenticated user password not as expected")
        
    def test_empty_config(self):
        src_file = test_utils.get_test_data_file("empty.cfg")
        self.assertRaises(InvalidUserParamsError, UserParameters, src_file)

    def test_partial_credential_config(self):
        src_file = test_utils.get_test_data_file("partial_creds.cfg")
        self.assertRaises(InvalidUserParamsError, UserParameters, src_file)
        
    def test_get_credentials_method(self):
        src_file = test_utils.get_test_data_file("complete_config.cfg")
        obj = UserParameters(src_file)
        (actual_user, actual_pass) = obj.credentials
        self.assertEqual(obj.username, actual_user, "username property should match the user returned by the get_credentials method")
        self.assertEqual(obj.password, actual_pass, "password property should match the user returned by the get_credentials method")
                
    def test_anonymous_get_credentials(self):
        src_file = test_utils.get_test_data_file("simple_config.cfg")
        obj = UserParameters(src_file)
        
        #quick sanity check - this sample config should be configured for anonymous access
        self.assertTrue(obj.anonymous_logon, "Sample data should be configured for anonymous access")
        
        self.assertEqual(None, obj.credentials, "Credentials for anonymous logons should be represented as None")

if __name__ == "__main__":
    unittest.main()