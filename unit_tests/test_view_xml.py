import unittest
from pyjen.utils.viewxml import ViewXML
import pytest

class view_xml_tests(unittest.TestCase):

    def test_rename(self):
        orig_xml = "<view><name>oldname</name></view>"
        new_name = "newname"
        expected_xml = "<view><name>{0}</name></view>".format(new_name)

        vxml = ViewXML(orig_xml)
        vxml.rename(new_name)
        self.assertIn(expected_xml, vxml.xml)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
