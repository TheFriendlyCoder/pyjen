from pyjen.build import build
import unittest
from mock import MagicMock
import pytest

class build_tests(unittest.TestCase):
        
    def test_get_build_number(self):
        expected_build_number = 3
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"number":expected_build_number}
        b = build(mock_data_io)
        
        self.assertEqual(b.get_build_number(), expected_build_number)
        
    def test_is_building(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"building":True}
        
        b = build(mock_data_io)
        self.assertTrue(b.is_building(), "Build should indicate that it is currently running")
        
    def test_is_not_building(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"building":False}
        
        b = build(mock_data_io)
        self.assertFalse(b.is_building(), "Build should indicate that it is not currently running")
        
    def test_get_console_output(self):
        expected_console_output = "Some sample console output"
        mock_data_io = MagicMock()
        mock_data_io.get_text.return_value = expected_console_output
        
        b = build(mock_data_io)
        
        self.assertEqual(b.get_console_output(), expected_console_output)
        mock_data_io.get_text.assert_called_once_with("/consoleText")

    def test_get_build_time(self):
        mock_data_io = MagicMock()
        #Build date: 12:03:17am Nov. 30, 2013
        mock_data_io.get_api_data.return_value = {"timestamp":1385784197000}
        
        b = build(mock_data_io)
        build_time = b.get_build_time()
        
        self.assertEqual(build_time.day, 30)
        self.assertEqual(build_time.month, 11)
        self.assertEqual(build_time.year, 2013)
        
        self.assertEqual(build_time.hour, 0)
        self.assertEqual(build_time.minute, 3)
        self.assertEqual(build_time.second, 17)
        
    def test_get_changeset(self):
        expected_scm_type = "svn"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"changeSet":{"kind":expected_scm_type,"items":[]}}
        
        b = build(mock_data_io)
        cs = b.get_changeset()
        
        self.assertEqual(cs.get_scm_type(), "svn")
        
if __name__ == "__main__":
    pytest.main()