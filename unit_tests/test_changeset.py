from pyjen.changeset import Changeset
import unittest
import pytest
from mock import MagicMock

class changeset_tests(unittest.TestCase):
        
    def test_get_scm_type(self):
        mock_controller = MagicMock()

        data = {}
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data, mock_controller)
        
        self.assertEqual("svn", cs.get_scm_type())
        
    def test_has_no_changes(self):
        mock_controller = MagicMock()

        data = {}
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data, mock_controller)
        
        self.assertFalse(cs.has_changes())
        
    def test_has_changes(self):
        mock_controller = MagicMock()

        data = {}
        data['kind'] = "svn"
        data['items'] = {"message":"Hello World"}
        cs = Changeset(data, mock_controller)
        
        self.assertTrue(cs.has_changes())

    def test_affected_items(self):
        expected_message = "Here is the commit log"
        mock_controller = MagicMock()

        data = {}
        data['kind'] = "svn"
        data['items'] = [{"msg":expected_message}]
        cs = Changeset(data, mock_controller)
        actual_items = cs.affected_items

        self.assertEqual(len(actual_items), 1)
        self.assertEqual(actual_items[0].message, expected_message)

    def test_actual_items_empty(self):
        mock_controller = MagicMock()

        data = {}
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data, mock_controller)
        actual_items = cs.affected_items

        self.assertIsNotNone(actual_items)
        self.assertEqual(len(actual_items), 0)

    def test_authors(self):
        expected_name = "John Doe"
        expected_url = "http://localhost:8080/user/jdoe"
        mock_user_controller = MagicMock()
        mock_user_controller.get_api_data.return_value = {"fullName":expected_name}

        mock_controller = MagicMock()
        mock_controller.clone.return_value = mock_user_controller

        data = {}
        data['kind'] = "svn"
        data['items'] = [{"author": {"absoluteUrl": expected_url, "fullName": expected_name}}]
        cs = Changeset(data, mock_controller)
        actual_items = cs.affected_items

        self.assertEqual(len(actual_items), 1)
        self.assertEqual(actual_items[0].author.full_name, expected_name)
        mock_controller.clone.assert_called_with(expected_url)
    
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
