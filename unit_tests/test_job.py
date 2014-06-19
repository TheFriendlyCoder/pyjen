import unittest
from pyjen.job import job
from mock import MagicMock
import pytest

class job_misc_tests(unittest.TestCase):
    """Tests for remaining utility methods of the job class not tested by other cases"""
    def test_get_name(self):
        expected_name = "MyJob1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':expected_name}
        
        j = job(mock_data_io)
        actual_name = j.get_name()

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")

    def test_start_build(self):
        mock_data_io = MagicMock()
        
        j = job (mock_data_io)
        j.start_build()
        
        mock_data_io.post.assert_called_once_with("/build")
        
    def test_disable(self):
        mock_data_io = MagicMock()
        
        j = job (mock_data_io)
        j.disable()
        
        mock_data_io.post.assert_called_once_with("/disable")

    def test_enable(self):
        mock_data_io = MagicMock()
        
        j = job (mock_data_io)
        j.enable()
        
        mock_data_io.post.assert_called_once_with("/enable")
        
    def test_is_disabled_true(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"disabled"}
        
        j = job (mock_data_io)
        self.assertTrue(j.is_disabled(), "Job should indicate that it is in a disabled state")
        
    def test_is_disabled_false(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"blue"}
        
        j = job (mock_data_io)
        self.assertFalse(j.is_disabled(), "Job should indicate that it is in an enabled state")
        
    def test_delete(self):
        mock_data_io = MagicMock()
        
        j = job (mock_data_io)
        j.delete()
        
        mock_data_io.post.assert_called_once_with("/doDelete")
    
    def test_has_been_built_true(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"notbuilt"}
        
        j = job (mock_data_io)
        self.assertFalse(j.has_been_built(), "Job should indicate that it has never been built")    

    def test_has_been_built_false(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"blue"}
        
        j = job (mock_data_io)
        self.assertTrue(j.has_been_built(), "Job should indicate that it has been built")

class job_dependencies_tests(unittest.TestCase):
    """Unit tests related to upstream and downstream dependency methods"""
    def test_no_downstream_jobs (self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[]}
        
        j = job (mock_data_io)
        dependencies = j.get_downstream_jobs()
        
        self.assertEqual(len(dependencies), 0, "Test job should not have any downstream dependencies")
    
    def test_one_downstream_job(self):
        # this one mock job depends on our job under test
        downstream_job_name = "j1"
        mock_dependent_job_data_io = MagicMock()
        mock_dependent_job_data_io.get_api_data.return_value = {"name":downstream_job_name}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[{"url":"http://localhost:8080/job/" + downstream_job_name}]}
        mock_data_io.clone.return_value = mock_dependent_job_data_io
        
        j = job (mock_data_io)
        dependencies = j.get_downstream_jobs()
        
        self.assertEqual(len(dependencies), 1, "Test job should have one downstream dependency")
        self.assertEqual(dependencies[0].get_name(), downstream_job_name)
        
    def test_multiple_downstream_jobs(self):
        
        # both jobs depend on the job under test
        downstream_job_name1 = "j1"
        downstream_job_url1 = "http://localhost:8080/job/" + downstream_job_name1
        downstream_job_name2 = "j2"
        downstream_job_url2 = "http://localhost:8080/job/" + downstream_job_name2

        def mock_clone(url):
            mock_dependent_job_data_io = MagicMock()
            if url == downstream_job_url1:
                mock_dependent_job_data_io.get_api_data.return_value = {"name":downstream_job_name1}
            elif url == downstream_job_url2:
                mock_dependent_job_data_io.get_api_data.return_value = {"name":downstream_job_name2}
            else:
                self.fail("unexpected input value given to mock clone function: " + url)
            return mock_dependent_job_data_io
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[{"url":downstream_job_url1},{"url":downstream_job_url2}]}
        mock_data_io.clone = mock_clone
                
        j = job (mock_data_io)
        dependencies = j.get_downstream_jobs()
        
        self.assertEqual(len(dependencies), 2, "Test job should have two downstream dependencies")
        names = []
        names.append(dependencies[0].get_name())
        names.append(dependencies[1].get_name())
        self.assertTrue(downstream_job_name1 in names, "Mock job #1 should be returned as a direct dependency")
        self.assertTrue(downstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")
       
    def test_multiple_downstream_jobs_recursive(self):
        
        # job j1 has no downstream dependencies
        downstream_job_name1 = "j1"
        downstream_job_url1 = "http://localhost:8080/job/" + downstream_job_name1
        mock_job1_data_io = MagicMock()
        mock_job1_data_io.get_api_data.return_value = {"name":downstream_job_name1, "downstreamProjects":[]}

        # job j2 triggers job j1
        downstream_job_name2 = "j2"
        downstream_job_url2 = "http://localhost:8080/job/" + downstream_job_name2 
        mock_job2_data_io = MagicMock()
        mock_job2_data_io.get_api_data.return_value = {"name":downstream_job_name2,"downstreamProjects":[{"url":downstream_job_url1}]}
        mock_job2_data_io.clone.return_value = mock_job1_data_io
        
        # our main job triggers job j2
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[{"url":downstream_job_url2}]}
        mock_data_io.clone.return_value = mock_job2_data_io
                
        # code under test 
        j = job (mock_data_io)
        dependencies = j.get_downstream_jobs(recursive=True)
        
        # validation
        self.assertEqual(len(dependencies), 2, "Test job should have two downstream dependencies")
        names = []
        names.append(dependencies[0].get_name())
        names.append(dependencies[1].get_name())
        self.assertTrue(downstream_job_name1 in names, "Mock job #1 should be returned as a transient dependency")
        self.assertTrue(downstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")


    def test_no_upstream_jobs (self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[]}
        
        j = job (mock_data_io)
        dependencies = j.get_upstream_jobs()
        
        self.assertEqual(len(dependencies), 0, "Test job should not have any upstream dependencies")
    
    def test_one_upstream_job(self):
        # our job under test depends directly on this one mock job
        upstream_job_name = "j1"
        mock_dependent_job_data_io = MagicMock()
        mock_dependent_job_data_io.get_api_data.return_value = {"name":upstream_job_name}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[{"url":"http://localhost:8080/job/" + upstream_job_name}]}
        mock_data_io.clone.return_value = mock_dependent_job_data_io
        
        j = job (mock_data_io)
        dependencies = j.get_upstream_jobs()
        
        self.assertEqual(len(dependencies), 1, "Test job should have one upstream dependency")
        self.assertEqual(dependencies[0].get_name(), upstream_job_name)
        
    def test_multiple_upstream_jobs(self):
        
        # our job under test directly depends on both of these jobs
        upstream_job_name1 = "j1"
        upstream_job_url1 = "http://localhost:8080/job/" + upstream_job_name1
        upstream_job_name2 = "j2"
        upstream_job_url2 = "http://localhost:8080/job/" + upstream_job_name2

        def mock_clone(url):
            mock_dependent_job_data_io = MagicMock()
            if url == upstream_job_url1:
                mock_dependent_job_data_io.get_api_data.return_value = {"name":upstream_job_name1}
            elif url == upstream_job_url2:
                mock_dependent_job_data_io.get_api_data.return_value = {"name":upstream_job_name2}
            else:
                self.fail("unexpected input value given to mock clone function: " + url)
            return mock_dependent_job_data_io
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[{"url":upstream_job_url1},{"url":upstream_job_url2}]}
        mock_data_io.clone = mock_clone
                
        j = job (mock_data_io)
        dependencies = j.get_upstream_jobs()
        
        self.assertEqual(len(dependencies), 2, "Test job should have two upstream dependencies")
        names = []
        names.append(dependencies[0].get_name())
        names.append(dependencies[1].get_name())
        self.assertTrue(upstream_job_name1 in names, "Mock job #1 should be returned as a direct dependency")
        self.assertTrue(upstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")
       
    def test_multiple_upstream_jobs_recursive(self):
        
        # job j1 has no upstream dependencies
        upstream_job_name1 = "j1"
        upstream_job_url1 = "http://localhost:8080/job/" + upstream_job_name1
        mock_job1_data_io = MagicMock()
        mock_job1_data_io.get_api_data.return_value = {"name":upstream_job_name1, "upstreamProjects":[]}

        # job j1 triggers job j2
        upstream_job_name2 = "j2"
        upstream_job_url2 = "http://localhost:8080/job/" + upstream_job_name2 
        mock_job2_data_io = MagicMock()
        mock_job2_data_io.get_api_data.return_value = {"name":upstream_job_name2,"upstreamProjects":[{"url":upstream_job_url1}]}
        mock_job2_data_io.clone.return_value = mock_job1_data_io
        
        # job j2 triggers our main job
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[{"url":upstream_job_url2}]}
        mock_data_io.clone.return_value = mock_job2_data_io
                
        # code under test 
        j = job (mock_data_io)
        dependencies = j.get_upstream_jobs(recursive=True)
        
        # validation
        self.assertEqual(len(dependencies), 2, "Test job should have two upstream dependencies")
        names = []
        names.append(dependencies[0].get_name())
        names.append(dependencies[1].get_name())
        self.assertTrue(upstream_job_name1 in names, "Mock job #1 should be returned as a transient dependency")
        self.assertTrue(upstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")
        

class build_methods_tests(unittest.TestCase):
    """Tests for build related methods exposed by the 'job' API"""
    def test_get_no_recent_builds(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"builds":[]}
 
        j = job (mock_data_io)
        builds = j.get_recent_builds()
        
        self.assertEqual(len(builds), 0, "Job object should not contain any valid builds")
    def test_get_one_recent_build(self):
        mock_build1_data_io = MagicMock()
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"builds":[{"url":"http://localhost:8080/job/j1/1"}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
        j = job (mock_data_io)
        builds = j.get_recent_builds()
        
        self.AssertEqual(len(builds), 1, "Job should have returned a single build")
        self.assertEqual(builds[0].get_build_number(), 7)
if __name__ == "__main__":
    pytest.main()