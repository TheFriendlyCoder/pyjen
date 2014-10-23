from pyjen.build import Build
import unittest
from mock import MagicMock
import pytest

class build_tests(unittest.TestCase):
        
    def test_get_build_number(self):
        expected_build_number = 3
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"number":expected_build_number}
        b = Build(mock_data_io)
        
        self.assertEqual(b.build_number, expected_build_number)
        
    def test_is_building(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"building":True}
        
        b = Build(mock_data_io)
        self.assertTrue(b.is_building, "Build should indicate that it is currently running")
        
    def test_is_not_building(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"building":False}
        
        b = Build(mock_data_io)
        self.assertFalse(b.is_building, "Build should indicate that it is not currently running")
        
    def test_get_console_output(self):
        expected_console_output = "Some sample console output"
        mock_data_io = MagicMock()
        mock_data_io.get_text.return_value = expected_console_output
        
        b = Build(mock_data_io)
        
        self.assertEqual(b.console_output, expected_console_output)
        mock_data_io.get_text.assert_called_once_with("/consoleText")

    def test_get_build_time(self):
        mock_data_io = MagicMock()
        #Build date: 12:03:17am Nov. 30, 2013
        mock_data_io.get_api_data.return_value = {"timestamp":1385784197000}
        
        b = Build(mock_data_io)
        build_time = b.build_time
        
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
        
        b = Build(mock_data_io)
        cs = b.get_changeset()
        
        self.assertEqual(cs.get_scm_type(), "svn")
    
    def test_get_culprits(self):
        expected_name = "John Doe"
        expected_url = "http://localhost:8080/user/jdoe"
        mock_user_data_io = MagicMock()
        mock_user_data_io.get_api_data.return_value = {"fullName":expected_name}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"culprits":[{"absoluteUrl":expected_url}]}
        mock_data_io.clone.return_value = mock_user_data_io
        
        b = Build(mock_data_io)
        culprits = b.culprits
        
        self.assertEqual(len(culprits), 1, "Mock build should have returns 1 breaker")
        self.assertEqual(culprits[0].full_name, expected_name)
        mock_data_io.clone.assert_called_once_with(expected_url)
        
    def test_get_culprits_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"culprits":[]}
        
        b = Build(mock_data_io)
        culprits = b.culprits
        
        self.assertEqual(len(culprits), 0, "Mock build should have no breakers")
        
    def test_build_equality(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"url":"www.someBuild.com"}
        first_build = Build(mock_data_io)
        second_build = Build(mock_data_io)
        self.assertEqual(second_build, first_build, "Build objects do not match when they should")
        
    def test_build_inequality(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"url":"www.someBuild.com"}
        first_build = Build(mock_data_io)
        
        mock_data_io2 = MagicMock()
        mock_data_io2.get_api_data.return_value = {"url":"www.someOtherBuild.com"}
        second_build = Build(mock_data_io2)
        self.assertNotEqual(second_build, first_build, "Build objects match when they should not")
        
        
if __name__ == "__main__":
    pytest.main()