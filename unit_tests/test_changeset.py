from pyjen.changeset import changeset
import unittest
import pytest

class changeset_tests(unittest.TestCase):
        
    def test_get_scm_type(self):
        data = {}
        data['kind'] = "svn"
        data['items'] = []
        cs = changeset(data)
        
        self.assertEqual("svn", cs.get_scm_type())
        
    def test_has_no_changes(self):
        data = {}
        data['kind'] = "svn"
        data['items'] = []
        cs = changeset(data)
        
        self.assertFalse(cs.has_changes())
        
    def test_has_changes(self):
        data = {}
        data['kind'] = "svn"
        data['items'] = {"message":"Hello World"}
        cs = changeset(data)
        
        self.assertTrue(cs.has_changes())
    
if __name__ == "__main__":
    pytest.main()