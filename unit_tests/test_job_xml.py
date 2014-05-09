from .xml_test_base import xml_test_case
from pyjen.utils.job_xml import job_xml
import unittest
from . import test_utils

class job_xml_tests(xml_test_case):
    """Test cases for the job_xml class"""
    
    def test_no_op(self):
        """Makes sure XML data is passed through the job_xml class unfettered"""
        
        source_xml_file = test_utils.get_sample_data_file("freestyle_basic_config.xml")
        f = open (source_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        
        j = job_xml(expected_xml)
        actual_xml = j.get_xml()
 
        self.assertEqualXML(expected_xml, actual_xml)
    
    
    def test_new_custom_workspace(self):
        """tests adding a new custom workspace to a job when no previous custom workspace exists"""
        
        source_xml_file = test_utils.get_sample_data_file("freestyle_basic_config.xml")
        f = open (source_xml_file, 'r')
        xml = f.read()
        f.close()
        
        expected_xml_file = test_utils.get_test_data_file("test_new_custom_workspace.xml")
        f = open (expected_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        
        j = job_xml(xml)
        j.set_custom_workspace('something/else')
        actual_xml = j.get_xml()
        
        self.assertEqualXML(expected_xml, actual_xml)
        
    def test_disable_custom_workspace(self):
        """tests removing custom workspace from a job"""
        
        source_xml_file = test_utils.get_sample_data_file("freestyle_customworkspace_config.xml")
        f = open (source_xml_file, 'r')
        xml = f.read()
        f.close()
        
        expected_xml_file = test_utils.get_test_data_file("test_disable_custom_workspace.xml")
        f = open (expected_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        
        j = job_xml(xml)
        j.disable_custom_workspace()
        actual_xml = j.get_xml()
        
        self.assertEqualXML(expected_xml, actual_xml)
        
        
        
if __name__ == '__main__':
    unittest.main()
