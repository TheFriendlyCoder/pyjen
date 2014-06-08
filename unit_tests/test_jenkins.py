import unittest
from pyjen.jenkins import jenkins
from mock import MagicMock

class jenkins_misc_tests(unittest.TestCase):
    """Tests for remaining utility methods of the Jenkins class not tested by other cases"""
    def test_get_version(self):
        expected_version = "1.2.3"
        
        mock_data_io = MagicMock()
        mock_data_io.get_headers.return_value = {'x-jenkins':expected_version}
        
        j = jenkins(mock_data_io)
        actual_version = j.get_version()

        self.assertEqual(expected_version, actual_version)
        self.assertEqual("call('/api/python')", str(mock_data_io.get_headers.call_args), 
                         "get_version method should have attempted to load HTTP header info from the api/python URL")
        self.assertEqual(mock_data_io.get_headers.call_count, 1, 
                                "get_headers method should have been called one time")
    
    def test_prepare_shutdown(self):
        mock_data_io = MagicMock()
        
        j = jenkins(mock_data_io)
        j.prepare_shutdown()
        
        self.assertEqual("call('/quietDown')", str(mock_data_io.post.call_args))
        self.assertEqual(mock_data_io.post.call_count, 1, "post method should have only been called once")
    
    def test_cancel_shutdown(self):
        mock_data_io = MagicMock()
        
        j = jenkins(mock_data_io)
        j.cancel_shutdown()
        
        self.assertEqual("call('/cancelQuietDown')", str(mock_data_io.post.call_args))
        self.assertEqual(mock_data_io.post.call_count, 1, "post method should have only been called once")
    
    def test_is_shutting_down(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"quietingDown":True}
        
        j = jenkins(mock_data_io)
        self.assertTrue(j.is_shutting_down(), "Object should be preparing for shutdown")
        
    def test_find_job_no_jobs(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'jobs':{}}
        
        j = jenkins(mock_data_io)
        njob = j.find_job("MyJob")
        self.assertEqual(njob, None, "No jobs should be found by the search method")
        
class jenkins_view_tests(unittest.TestCase):
    """Unit tests for the view-related methods of the Jenkins class"""
    
    def setUp(self):
        """Configure a mock dataio object which supports a few mock view objects"""
        self.primary_view_name = 'main'
        jenkins_root_url = 'http://localhost:8080/'
        self.primary_view_url = jenkins_root_url + "view/" + self.primary_view_name
        self.view2_name = 'secondView'
        self.view2_url = 'http://localhost:8080/view/secondView'
            
        # io objects used by the two views managed by our mock Jenkins instance
        self.mock_primary_view_data_io = MagicMock()
        self.mock_primary_view_data_io.get_api_data.return_value = {'name':self.primary_view_name}
        self.mock_view2_data_io = MagicMock()
        self.mock_view2_data_io.get_api_data.return_value = {'name':self.view2_name}
        
        # mock jenkins instance which exposes 2 views
        mock_jenkins_data_io = MagicMock()
        mock_views = []
        mock_views.append({'url':self.view2_url,'name':self.view2_name})
        mock_views.append({'url':jenkins_root_url,'name':self.primary_view_name})
        mock_jenkins_data_io.get_api_data.return_value = {'views':mock_views,'primaryView':mock_views[1]}
        mock_jenkins_data_io.clone.side_effect = self.mock_clone
        
        self._mock_jenkins_data_io = mock_jenkins_data_io
        
    def mock_clone(self, url):
        if url == self.primary_view_url:
            return self.mock_primary_view_data_io
        if url == self.view2_url:
            return self.mock_view2_data_io
        return None
    
    def test_get_default_view(self):        
        # test logic
        j = jenkins(self._mock_jenkins_data_io)
        v = j.get_default_view()
        actual_view_name = v.get_name()
        
        # verification
        self.assertEqual(actual_view_name, self.primary_view_name)
        self._mock_jenkins_data_io.clone.assert_called_with(self.primary_view_url)
    
    def test_get_multiple_views(self):
        # test logic
        j = jenkins(self._mock_jenkins_data_io)
        views = j.get_views()
        
        # verification
        self.assertEqual(len(views), 2)
        self.assertEqual(views[0].get_name(), self.view2_name)
        self.assertEqual(views[1].get_name(), self.primary_view_name)
    
    def test_find_view(self):
        # test logic
        j = jenkins(self._mock_jenkins_data_io)
        view = j.find_view(self.view2_name)
        
        # verification
        self.assertNotEqual(view, None, "code should return a valid pyjen.view object")
        self.assertEqual(view.get_name(), self.view2_name, "incorrect view returned by jenkins object")
        self._mock_jenkins_data_io.clone.assert_called_once_with(self.view2_url)
        
    def test_get_view_primary_view(self):        
        # test logic
        j = jenkins(self._mock_jenkins_data_io)
        view = j.find_view(self.primary_view_name)
        
        # verification
        self.assertNotEqual(view, None, "code should return a valid pyjen.view object")
        self.assertEqual(view.get_name(), self.primary_view_name, "incorrect view returned by jenkins object")
        self._mock_jenkins_data_io.clone.assert_called_once_with(self.primary_view_url)
    
    def test_find_missing_view(self):
        # test logic
        j = jenkins(self._mock_jenkins_data_io)
        view = j.find_view("DoesNotExist")
    
        # verification
        self.assertEqual(view, None, "No valid view should have been found.")
        
if __name__ == "__main__":
    unittest.main()
    