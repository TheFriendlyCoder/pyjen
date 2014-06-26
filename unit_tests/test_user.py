from pyjen.user import user
import unittest
from mock import MagicMock
import pytest

class user_tests(unittest.TestCase):
    def test_get_user_id(self):
        expected_id = "myuserid"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"id":expected_id}
        
        u = user(mock_data_io)
        
        self.assertEqual(u.user_id, expected_id)
    
    def test_get_full_username(self):
        expected_name = "John Doe"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"fullName":expected_name}
        
        u = user(mock_data_io)
        
        self.assertEqual(u.full_name, expected_name)
        
    def test_get_description(self):
        expected_desc = "This user has some sort of role"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"description":expected_desc}
        
        u = user(mock_data_io)
        
        self.assertEqual(u.description, expected_desc)
        
    def test_get_no_description(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"description":None}
        
        u = user(mock_data_io)
        
        self.assertEqual(u.description, None)
            
    def test_get_email(self):
        expected_email = "john.doe@foo.bar.com"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"property":[{"address":expected_email}]}
        
        u = user(mock_data_io)
        
        self.assertEqual(u.email, expected_email)
    
if __name__ == "__main__":
    pytest.main()