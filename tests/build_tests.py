from pyjen.build import build
import unittest
from mock_data_requester import mock_data_requester

class build_tests(unittest.TestCase):
    def test_get_changeset(self):
        src = mock_data_requester("/home/kevin/Desktop/git_changeset_sample.txt")
        bld = build('', custom_data_requester=src)
        change = bld.get_changeset()
        
        change.get_items()
        
if __name__ == "__main__":
    unittest.main()