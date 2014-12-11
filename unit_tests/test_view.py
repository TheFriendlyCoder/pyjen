from pyjen.view import View
import unittest
import pytest
from mock import MagicMock, PropertyMock

class vView(View):
    type = ""


class view_tests(unittest.TestCase):
    
    def test_get_name(self):
        expected_name = "MyView1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':expected_name}
        
        v = vView(mock_data_io, None)
        actual_name = v.name

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")

    def test_supported_types(self):
        actual_types = View.supported_types()

        self.assertIn("hudson.model.ListView", actual_types)
        self.assertIn("hudson.model.AllView", actual_types)
        self.assertIn("hudson.model.MyView", actual_types)

        self.assertGreater(len(actual_types), 3)

    def test_job_count(self):
        mock_data_io = MagicMock()
        jobs = []
        jobs.append({'url':'foo'})
        jobs.append({'url':'bar'})
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':jobs}
        
        v = vView(mock_data_io, None)
        expected_count = v.job_count

        self.assertEqual(expected_count, 2, "There should be 2 jobs in the mock view")
        
    
    def test_get_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        job2_url = 'http://localhost:8080/job/j2'
        job2_name = 'j2'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.config_xml = "<project></project>"
        mock_job2_dataio = MagicMock()
        mock_job2_dataio.get_api_data.return_value = {"name":job2_name}
        mock_job2_dataio.config_xml = "<project></project>"
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url},{'url':job2_url}]}
        def mock_clone(new_url):
            if new_url == job1_url: return mock_job1_dataio
            if new_url == job2_url: return mock_job2_dataio
            self.fail("Unknown source URL provided to clone method: " + new_url)
        mock_data_io.clone.side_effect = mock_clone
            
        v = vView(mock_data_io, None)
        jobs = v.jobs
        
        self.assertEqual(len(jobs), 2, "view should have 2 jobs contained within it")
        self.assertEqual(jobs[0].name, job1_name)
        self.assertEqual(jobs[1].name, job2_name)
        
    def test_get_jobs_no_jobs(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[]}
            
        v = vView(mock_data_io, None)
        jobs = v.jobs
        
        self.assertEqual(len(jobs), 0, "view should not have any jobs contained within it")
        
    def test_get_config_xml(self):
        expected_xml = "<sample_xml/>"

        p = PropertyMock(return_value=expected_xml)
        mock_data_io = MagicMock()
        type(mock_data_io).config_xml = p
        
        v = vView(mock_data_io, None)
        actual_xml = v.config_xml
        
        self.assertEqual(actual_xml, expected_xml)
        p.assert_called_once_with()

    def test_delete_view(self):
        mock_data_io = MagicMock()
        
        v = vView(mock_data_io, None)
        v.delete()
        
        mock_data_io.post.assert_called_once_with("/doDelete")
    
    def test_set_config_xml(self):
        expected_config_xml = "<Sample Config XML/>"
        mock_data_io = MagicMock()
        p = PropertyMock(return_value=expected_config_xml)
        type(mock_data_io).config_xml = p

        v = vView(mock_data_io, None)
        v.config_xml = expected_config_xml

        self.assertEqual(p.call_count, 1)
        p.assert_called_once_with(expected_config_xml)

    def test_delete_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url, 'name':job1_name}]}
        mock_data_io.clone.return_value = mock_job1_dataio

        v = vView(mock_data_io, None)
        v.delete_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/doDelete")

    def test_disable_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url, 'name':job1_name}]}
        mock_data_io.clone.return_value = mock_job1_dataio

        v = vView(mock_data_io, None)
        v.disable_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/disable")
        
    def test_enable_all_jobs(self):
        job1_url = 'http://localhost:8080/job/j1'
        job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':job1_url, 'name':job1_name}]}
        mock_data_io.clone.return_value = mock_job1_dataio
            
        v = vView(mock_data_io, None)
        v.enable_all_jobs()
        
        mock_job1_dataio.post.assert_called_once_with("/enable")

    def test_clone_all_jobs(self):
        new_job_name = "new_job"
        orig_job_name = "original_job"

        mock_job_controller = MagicMock()
        mock_job_controller.get_text.return_value = "<project></project>"
        mock_job_controller.get_api_data.return_value = {"name":orig_job_name}

        mock_view_controller = MagicMock()
        mock_view_controller.get_api_data.return_value = {"jobs":[{"url":"http://fake/job/original_job","name":orig_job_name}]}
        mock_view_controller.clone.return_value = mock_job_controller

        mock_new_job = MagicMock()
        mock_new_job.name = new_job_name

        mock_jenkins = MagicMock()
        mock_jenkins._clone_job.return_value = mock_new_job

        v = vView(mock_view_controller, mock_jenkins)
        v.clone_all_jobs(orig_job_name, new_job_name)

        mock_jenkins._clone_job.assert_called_once_with(orig_job_name, new_job_name)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
