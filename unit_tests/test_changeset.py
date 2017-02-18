from pyjen.changeset import Changeset
import unittest
import pytest
from mock import MagicMock

class changeset_tests(unittest.TestCase):
        
    def test_get_scm_type(self):
        data = dict()
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data)
        
        self.assertEqual("svn", cs.scm_type)
        
    def test_has_no_changes(self):
        data = dict()
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data)
        
        self.assertFalse(cs.has_changes)
        
    def test_has_changes(self):
        data = dict()
        data['kind'] = "svn"
        data['items'] = {"message": "Hello World"}
        cs = Changeset(data)
        
        self.assertTrue(cs.has_changes)

    def test_affected_items(self):
        expected_message = "Here is the commit log"

        data = dict()
        data['kind'] = "svn"
        data['items'] = [{"msg": expected_message}]
        cs = Changeset(data)
        actual_items = cs.affected_items

        self.assertEqual(len(actual_items), 1)
        self.assertEqual(actual_items[0].message, expected_message)

    def test_actual_items_empty(self):
        data = dict()
        data['kind'] = "svn"
        data['items'] = []
        cs = Changeset(data)
        actual_items = cs.affected_items

        self.assertIsNotNone(actual_items)
        self.assertEqual(len(actual_items), 0)

    def test_authors(self):
        expected_url = "http://localhost:8080/user/jdoe/"

        data = dict()
        data['kind'] = "svn"
        data['items'] = [{"author": {"absoluteUrl": expected_url, "fullName": "John Doe"}}]
        cs = Changeset(data)
        actual_items = cs.affected_items

        self.assertEqual(len(actual_items), 1)
        self.assertEqual(actual_items[0].author.url, expected_url)
    
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
