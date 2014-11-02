from pyjen.view import View
import unittest
import pytest
from mock import MagicMock

class view_tests(unittest.TestCase):
    
    def test_get_name(self):
        expected_name = "MyView1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':expected_name}
        
        v = View(mock_data_io, None)
        actual_name = v.name

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")
    def test_job_count(self):
        mock_data_io = MagicMock()
        jobs = []
        jobs.append({'url':'foo'})
        jobs.append({'url':'bar'})
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':jobs}
        
        v = View(mock_data_io, None)
        expected_count = v.job_count

        self.assertEqual(expected_count, 2, "There should be 2 jobs in the mock view")
        
    
    def test_get_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        job2_url = 'http://localhost:8080/job/j2'
        job2_name = 'j2'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"
        mock_job2_dataio = MagicMock()
        mock_job2_dataio.get_api_data.return_value = {"name":job2_name}
        mock_job2_dataio.get_text.return_value = "<project></project>"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url},{'url':job2_url}]}
        def mock_clone(new_url):
            if new_url == job1_url: return mock_job1_dataio
            if new_url == job2_url: return mock_job2_dataio
            self.fail("Unknown source URL provided to clone method: " + new_url)
        mock_data_io.clone.side_effect = mock_clone
            
        v = View(mock_data_io, None)
        jobs = v.jobs
        
        self.assertEqual(len(jobs), 2, "view should have 2 jobs contained within it")
        self.assertEqual(jobs[0].name, job1_name)
        self.assertEqual(jobs[1].name, job2_name)
        
    def test_get_jobs_no_jobs(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[]}
            
        v = View(mock_data_io, None)
        jobs = v.jobs
        
        self.assertEqual(len(jobs), 0, "view should not have any jobs contained within it")
        
    def test_get_config_xml(self):
        expected_xml = "<sample_xml/>"
        mock_data_io = MagicMock()
        mock_data_io.get_text.return_value = expected_xml
        
        v = View(mock_data_io, None)
        actual_xml = v.config_xml
        
        self.assertEqual(actual_xml, expected_xml)
        mock_data_io.get_text.assert_called_once_with("/config.xml")
   
    def test_delete_view(self):
        mock_data_io = MagicMock()
        
        v = View(mock_data_io, None)
        v.delete()
        
        mock_data_io.post.assert_called_once_with("/doDelete")
    
    def test_set_config_xml(self):
        expected_config_xml = "<Sample Config XML/>"
        mock_data_io = MagicMock()
        
        v = View (mock_data_io, None)
        v.set_config_xml(expected_config_xml)
        
        self.assertEqual(mock_data_io.post.call_count, 1)
        self.assertEqual(mock_data_io.post.call_args[0][0], "/config.xml")
        post_data = mock_data_io.post.call_args[0][1]
        self.assertTrue('data' in post_data.keys())
        self.assertEqual(post_data['data'], expected_config_xml)

    def test_delete_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url}]}
        mock_data_io.clone.return_value = mock_job1_dataio
            
        v = View(mock_data_io, None)
        v.delete_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/doDelete")

    def test_disable_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url}]}
        mock_data_io.clone.return_value = mock_job1_dataio
            
        v = View(mock_data_io, None)
        v.disable_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/disable")
        
    def test_enable_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url}]}
        mock_data_io.clone.return_value = mock_job1_dataio
            
        v = View(mock_data_io, None)
        v.enable_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/enable")
        
if __name__ == "__main__":
    pytest.main()