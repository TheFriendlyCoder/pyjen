import unittest
from pyjen.utils.job_xml import job_xml
import xml.etree.ElementTree as ElementTree
from os import path

class xml_test_case(unittest.TestCase):
    def assertEqualXML(self, expected, actual):
        """Compares two XML encoded character strings
        
        This helper method does a basic tree comparison between
        the two XML strings. This includes comparing all nodes
        in the tree, their associated attributes and text content,
        and children (recursively).
        
        If the validation detects any differences, an appropriate
        unit test exception will be thrown including some helpful
        contextual information about the error.
        
        Parameters
        ----------
        expected : string
            the expected XML data tree to be compared
        actual : string
            the actual or produced XML data tree for the comparison
        """
        expected_ele = ElementTree.fromstring(expected)
        actual_ele = ElementTree.fromstring(actual)
        
        self.__compareXMLElements(expected_ele, actual_ele)
        
        
        
    def __compareXMLElements(self, expected, actual):
        """Compares the attributes of two elements
        
        Helper method used by the assertEqualXML method.
        Compares the attributes and text data for both
        elements, then recursively compares any associated
        sub-elements contained therein.
        
        Parameters:
        expected : xml.etree.ElementTree
            the element containing the expected XML attributes
        actual : xml.etree.ElementTree
            the element containing the produced or generated XML attributes
        """
        #Compare this elements properties
        self.assertEqual(expected.tag, actual.tag, "Tags should be equivalent: " + expected.tag)
        
        if expected.text == None and not actual.text == None:
            self.fail("Tag '" + expected.tag + "' has text declaration in actual tree but not expected: " + actual.text) 
        elif not expected.text == None and actual.text == None:
            self.fail("Tag '" + expected.tag + "' has text declaration in expected tree but not actual: " + expected.text)
        elif not expected.text == None and not actual.text == None:
            self.assertEqual(expected.text.strip(), actual.text.strip(), expected.tag + " tags should contain the same text data: " + expected.text.strip())
        
        self.__compareXMLAttributes(expected, actual)
        
        #recursively check all children
        expected_children = expected.getchildren()
        
        for echild in expected_children:
            
            achild = actual.find(echild.tag)
            self.assertTrue(achild != None, "Expected child element not found in actual tree: " + echild.tag)
            
            self.__compareXMLElements(echild, achild)
            
        #As a shortcut to detecting other discrepancies between the trees, 
        #just check to see if they have the same number of children. If not there
        #must be one or more nodes in the actual tree not in the expected 
        actual_children = actual.getchildren()
        self.assertEqual(len(expected_children), len(actual_children), "Tag '" + expected.tag + "' has different numbers of children")        
        
        
        
    def __compareXMLAttributes(self, expected, actual):
        """Compares attributes of two XML elements
        
        Helper method used by __compareXMLElements. Compares any
        XML attributes associated with each element, reporting
        differences in available attributes as well as their
        associated values.
        
        Parameters
        ----------
        expected : xml.etree.ElementTree
            XML object with the expected set of attributes + values
        actual
            XML object with the generated or produced attributes and values to be compared
        """
        for eatt in expected.attrib:
            if actual.attrib.has_key(eatt):
                self.assertEqual(expected.attrib[eatt], actual.attrib[eatt], "Attribute '" + eatt + "' of tag '" + expected.tag + "' should have equivalent values")
            else:
                self.fail("Expected attribute not found: " + eatt)
                
        self.assertEqual(len(expected.attrib), len(actual.attrib), "Tag " + expected.tag + " has different number of attribute between the trees.")



    def get_sample_data_file(self, filename):
        """Given a filename, this method generates the full path to the file in the sample data folder
    
        This method assumes that sample data is source data that
        typically represents data found in the real world under
        typical use of Jenkins. These files should never be modified
        during unit test execution.
        
        This method does basic validation to ensure the specified
        sample data file does exist. If it does not an appropriate
        unit test exception will be thrown.
        
        Parameters
        ----------
        filename : string
            name of the file to be located
        
        Returns
        -------
        string
            Full path and file name of the sample data to be loaded
        """
        
        working_path = path.dirname(path.realpath(__file__))
        retval =  working_path + "/sample_data/" + filename
        
        self.assertTrue(path.exists(retval), "Requested sample data file doesn't exist: " + retval)
        
        return retval

    def get_test_data_file(self, filename):
        """Given a filename, this method generates the full path to the file in the test data folder
        
        Test data is considered miscellaneous unit test data, such
        as those used to validate the output of a process under test.
        
        This method does basic validation to ensure the specified
        test data file does exist. If it does not an appropriate
        unit test exception will be thrown.
        
        Parameters
        ----------
        filename : string
            name of the file to be located
        
        Returns
        -------
        string
            Full path and file name of the test data to be loaded
        """
        
        working_path = path.dirname(path.realpath(__file__))
        retval =  working_path + "/test_data/" + filename
        
        self.assertTrue(path.exists(retval), "Requested sample data file doesn't exist: " + retval)
        
        return retval
    
    
    
    
    
class job_xml_tests(xml_test_case):
    """Test cases for the job_xml class"""
    
    def test_no_op(self):
        """Makes sure XML data is passed through the job_xml class unfettered"""
        
        source_xml_file = self.get_sample_data_file("freestyle_basic_config.xml")
        f = open (source_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        j = job_xml(expected_xml)
        actual_xml = j.get_xml()
 
        self.assertEqualXML(expected_xml, actual_xml)
    
    
    def test_new_custom_workspace(self):
        """tests adding a new custom workspace to a job when no previous custom workspace exists"""
        
        source_xml_file = self.get_sample_data_file("freestyle_basic_config.xml")
        f = open (source_xml_file, 'r')
        xml = f.read()
        f.close()
        
        expected_xml_file = self.get_test_data_file("test_new_custom_workspace.xml")
        f = open (expected_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        
        j = job_xml(xml)
        j.set_custom_workspace('something/else')
        actual_xml = j.get_xml()
        
        self.assertEqualXML(expected_xml, actual_xml)
        
    def test_disable_custom_workspace(self):
        """tests removing custom workspace from a job"""
        
        source_xml_file = self.get_sample_data_file("freestyle_customworkspace_config.xml")
        f = open (source_xml_file, 'r')
        xml = f.read()
        f.close()
        
        expected_xml_file = self.get_test_data_file("test_disable_custom_workspace.xml")
        f = open (expected_xml_file, 'r')
        expected_xml = f.read()
        f.close()
        
        j = job_xml(xml)
        j.disable_custom_workspace()
        actual_xml = j.get_xml()
        
        self.assertEqualXML(expected_xml, actual_xml)
        
        
        
if __name__ == '__main__':
    unittest.main()
