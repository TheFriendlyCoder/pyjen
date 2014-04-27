from pyjen.user_params import UserParameters
from pyjen.exceptions import InvalidUserParamsError

import test_utils
import unittest

class UserParameters_tests(unittest.TestCase):
    def test_simple_config(self):
        src_file = test_utils.get_test_data_file("simple_config.cfg")
        obj = UserParameters(src_file)
        self.assertEquals(obj.url, "http://MyServer/jenkins", "Parsed URL not as expected")
        self.assertTrue(obj.anonymous_logon,  "Should have anonymous logon enabled")
        
    def test_complete_config(self):
        src_file = test_utils.get_test_data_file("complete_config.cfg")
        obj = UserParameters(src_file)
        self.assertEquals(obj.url, "http://MyServer/jenkins", "Parsed URL not as expected")
        self.assertFalse(obj.anonymous_logon,  "Should have anonymous logon disbled")
        self.assertEquals(obj.username, "MyUser", "Authenticated user name not as expected")
        self.assertEquals(obj.password, "MyPassword!", "Authenticated user password not as expected")
        
    def test_empty_config(self):
        src_file = test_utils.get_test_data_file("empty.cfg")
        self.assertRaises(InvalidUserParamsError, UserParameters, src_file)

    def test_partial_credential_config(self):
        src_file = test_utils.get_test_data_file("partial_creds.cfg")
        self.assertRaises(InvalidUserParamsError, UserParameters, src_file)
        
if __name__ == "__main__":
    unittest.main()