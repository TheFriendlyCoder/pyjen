from pyjen.build import build
import unittest
from mock_data_requester import file_based_requester
import test_utils
from datetime import datetime

class build_tests(unittest.TestCase):
    def test_get_build_time(self):
        bld = build(test_utils.get_sample_data_file("build_with_svn_changeset.txt"), file_based_requester)
        
        #Build date: 12:03:17am Nov. 30, 2013
        self.assertEqual(datetime.fromtimestamp(1385784197.000), bld.get_build_time())
        
    def test_is_not_building(self):
        bld = build(test_utils.get_sample_data_file("build_with_svn_changeset.txt"), file_based_requester)
        
        self.assertFalse(bld.is_building(), "Sample build project should not be building")
        
    def test_get_build_number(self):
        bld = build(test_utils.get_sample_data_file("build_with_svn_changeset.txt"), file_based_requester)
        self.assertEqual(169, bld.get_build_number())
        


class changeset_tests(unittest.TestCase):
    def test_get_changeset_svn(self):
        bld = build(test_utils.get_sample_data_file("build_with_svn_changeset.txt"), file_based_requester)
        
        change = bld.get_changeset()
        
        self.assertEqual("svn", change.get_scm_type())
        items = change.get_affected_items()
        
        self.assertEqual(2, len(items))
        
        item1 = items[0]
        self.assertEqual('Jane Doe', item1['author'])
        self.assertEqual('http://jenkins/user/janedoe', item1['authorUrl'])
        self.assertEqual('987654', item1['commitId'])
        self.assertEqual('some other commit\\with some details', item1['message'])
        self.assertEqual(datetime.fromtimestamp(1385758513.358), item1['time'])
        self.assertEqual(1, len(item1['changes']))
        self.assertEqual('edit', item1['changes'][0]['editType'])
        self.assertEqual('/another/path/to/file.pdf', item1['changes'][0]['file'])
        
        item2 = items[1]
        self.assertEqual('John Doe', item2['author'])
        self.assertEqual('http://jenkins/user/johndoe', item2['authorUrl'])
        self.assertEqual('123456', item2['commitId'])
        self.assertEqual('changed one thing\\then another', item2['message'])
        self.assertEqual(datetime.fromtimestamp(1385755849.290), item2['time'])
        self.assertEqual(2, len(item2['changes']))
        self.assertEqual('edit', item2['changes'][0]['editType'])
        self.assertEqual('/path/to/file1.txt', item2['changes'][0]['file'])
        self.assertEqual('add', item2['changes'][1]['editType'])
        self.assertEqual('/path/to/another/file2.pdf', item2['changes'][1]['file'])
                
    def test_get_scm_type(self):
        bld = build(test_utils.get_sample_data_file("build_with_svn_changeset.txt"), file_based_requester)
        
        change = bld.get_changeset()
        
        self.assertEqual("svn", change.get_scm_type())
        
if __name__ == "__main__":
    unittest.main()