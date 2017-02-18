import unittest
from pyjen.job import Job
from mock import MagicMock, PropertyMock
import pytest
from datetime import datetime


class vJob(Job):
    type = ""


class job_misc_tests(unittest.TestCase):
    """Tests for remaining utility methods of the Job class not tested by other cases"""
    def test_get_name(self):
        expected_name = "MyJob1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':expected_name}
        
        j = vJob(mock_data_io, None)
        actual_name = j.name

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")

    def test_start_build(self):
        mock_data_io = MagicMock()
        
        j = vJob (mock_data_io, None)
        j.start_build()
        
        mock_data_io.post.assert_called_once_with("/build")
        
    def test_disable(self):
        mock_data_io = MagicMock()
        
        j = vJob (mock_data_io, None)
        j.disable()
        
        mock_data_io.post.assert_called_once_with("/disable")

    def test_enable(self):
        mock_data_io = MagicMock()
        
        j = vJob (mock_data_io, None)
        j.enable()
        
        mock_data_io.post.assert_called_once_with("/enable")
        
    def test_is_disabled_true(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"disabled"}
        
        j = vJob (mock_data_io, None)
        self.assertTrue(j.is_disabled, "Job should indicate that it is in a disabled state")
        
    def test_is_disabled_false(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"blue"}
        
        j = vJob (mock_data_io, None)
        self.assertFalse(j.is_disabled, "Job should indicate that it is in an enabled state")
        
    def test_delete(self):
        mock_data_io = MagicMock()
        
        j = vJob (mock_data_io, None)
        j.delete()
        
        mock_data_io.post.assert_called_once_with("/doDelete")
    
    def test_has_been_built_true(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"notbuilt"}
        
        j = vJob (mock_data_io, None)
        self.assertFalse(j.has_been_built, "Job should indicate that it has never been built")    

    def test_has_been_built_false(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"color":"blue"}
        
        j = vJob (mock_data_io, None)
        self.assertTrue(j.has_been_built, "Job should indicate that it has been built")
        
    def test_get_config_xml(self):
        expected_config_xml = "<Sample Config XML/>"
        p = PropertyMock(return_value=expected_config_xml)
        mock_data_io = MagicMock()
        type(mock_data_io).config_xml = p

        j = vJob (mock_data_io, None)
        
        self.assertEqual(j.config_xml, expected_config_xml)
        p.assert_called_with()

    def test_set_config_xml(self):
        expected_config_xml = "<Sample Config XML/>"
        p = PropertyMock(return_value=expected_config_xml)
        mock_data_io = MagicMock()
        type(mock_data_io).config_xml = p

        j = vJob(mock_data_io, None)
        j.config_xml = expected_config_xml
        
        self.assertEqual(p.call_count, 1)
        p.assert_called_once_with(expected_config_xml)

    def test_clone(self):
        new_job_name = "ClonedJob"
        cur_job_name = "OriginalJob"

        # Mock jenkins interface with mocked methods used by clone method
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"name":cur_job_name}

        # Mock for new job generated by the clone method
        mock_new_job = MagicMock()
        mock_new_job.name = new_job_name

        # Mock Jenkins object, which is used by the 'clone' method to perform the actual action
        mock_jenkins = MagicMock()
        mock_jenkins._clone_job.return_value = mock_new_job

        jb = vJob(mock_data_io, mock_jenkins)
        newjob = jb.clone(new_job_name)

        # Make sure the Jenkins clone job method was called, which performs the clone
        mock_jenkins._clone_job.assert_called_once_with(cur_job_name, new_job_name)

    def test_supported_types(self):
        actual = Job.supported_types()

        self.assertIn("project", actual)
        self.assertGreater(len(actual), 1)

class job_dependencies_tests(unittest.TestCase):
    """Unit tests related to upstream and downstream dependency methods"""
    def test_no_downstream_jobs (self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[]}
        
        j = vJob (mock_data_io, None)
        dependencies = j.downstream_jobs
        
        self.assertEqual(len(dependencies), 0, "Test job should not have any downstream dependencies")
    
    def test_one_downstream_job(self):
        # this one mock job depends on our job under test
        downstream_job_name = "j1"
        mock_dependent_job_data_io = MagicMock()
        mock_dependent_job_data_io.get_api_data.return_value = {"name":downstream_job_name}
        mock_dependent_job_data_io.config_xml = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[{"url":"http://localhost:8080/job/" + downstream_job_name}]}
        mock_data_io.clone.return_value = mock_dependent_job_data_io
        
        j = vJob (mock_data_io, None)
        dependencies = j.downstream_jobs
        
        self.assertEqual(len(dependencies), 1, "Test job should have one downstream dependency")
        self.assertEqual(dependencies[0].name, downstream_job_name)
        
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

            mock_dependent_job_data_io.config_xml = "<project></project>"
            return mock_dependent_job_data_io
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects":[{"url":downstream_job_url1},{"url":downstream_job_url2}]}
        mock_data_io.clone = mock_clone
                
        j = vJob(mock_data_io, None)
        dependencies = j.downstream_jobs
        
        self.assertEqual(len(dependencies), 2, "Test job should have two downstream dependencies")
        names = []
        names.append(dependencies[0].name)
        names.append(dependencies[1].name)
        self.assertTrue(downstream_job_name1 in names, "Mock job #1 should be returned as a direct dependency")
        self.assertTrue(downstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")
       
    def test_multiple_downstream_jobs_recursive(self):
        
        # job j1 has no downstream dependencies
        downstream_job_name1 = "j1"
        downstream_job_url1 = "http://localhost:8080/job/" + downstream_job_name1
        mock_job1_data_io = MagicMock()
        mock_job1_data_io.get_api_data.return_value = {"name":downstream_job_name1, "downstreamProjects":[]}
        mock_job1_data_io.config_xml = "<project></project>"

        # job j2 triggers job j1
        downstream_job_name2 = "j2"
        downstream_job_url2 = "http://localhost:8080/job/" + downstream_job_name2 
        mock_job2_data_io = MagicMock()
        mock_job2_data_io.get_api_data.return_value = {"name":downstream_job_name2,"downstreamProjects":[{"url":downstream_job_url1}]}
        mock_job2_data_io.clone.return_value = mock_job1_data_io
        mock_job2_data_io.config_xml = "<project></project>"

        # job j3 triggers job j2
        downstream_job_name3 = "j3"
        downstream_job_url3 = "http://localhost:8080/job/" + downstream_job_name3
        mock_job3_data_io = MagicMock()
        mock_job3_data_io.get_api_data.return_value = {"name": downstream_job_name3, "downstreamProjects": [{"url": downstream_job_url2}]}
        mock_job3_data_io.clone.return_value = mock_job2_data_io
        mock_job3_data_io.config_xml = "<project></project>"

        # our main job triggers job j3
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"downstreamProjects": [{"url": downstream_job_url3}]}
        mock_data_io.clone.return_value = mock_job3_data_io
                
        # code under test 
        j = vJob(mock_data_io, None)
        dependencies = j.all_downstream_jobs
        
        # validation
        self.assertEqual(len(dependencies), 3, "Test job should have three downstream dependencies")
        names = []
        names.append(dependencies[0].name)
        names.append(dependencies[1].name)
        names.append(dependencies[2].name)
        self.assertTrue(downstream_job_name1 in names, "Mock job #1 should be returned as a transient dependency")
        self.assertTrue(downstream_job_name2 in names, "Mock job #2 should be returned as a transient dependency")
        self.assertTrue(downstream_job_name3 in names, "Mock job #3 should be returned as a direct dependency")

    def test_no_upstream_jobs (self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[]}
        
        j = vJob (mock_data_io, None)
        dependencies = j.upstream_jobs
        
        self.assertEqual(len(dependencies), 0, "Test job should not have any upstream dependencies")
    
    def test_one_upstream_job(self):
        # our job under test depends directly on this one mock job
        upstream_job_name = "j1"
        mock_dependent_job_data_io = MagicMock()
        mock_dependent_job_data_io.get_api_data.return_value = {"name":upstream_job_name}
        mock_dependent_job_data_io.config_xml = "<project></project>"

        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[{"url":"http://localhost:8080/job/" + upstream_job_name}]}
        mock_data_io.clone.return_value = mock_dependent_job_data_io
        
        j = vJob (mock_data_io, None)
        dependencies = j.upstream_jobs
        
        self.assertEqual(len(dependencies), 1, "Test job should have one upstream dependency")
        self.assertEqual(dependencies[0].name, upstream_job_name)
        
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
            mock_dependent_job_data_io.config_xml = "<project></project>"
            return mock_dependent_job_data_io
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects":[{"url":upstream_job_url1},{"url":upstream_job_url2}]}
        mock_data_io.clone = mock_clone
                
        j = vJob (mock_data_io, None)
        dependencies = j.upstream_jobs
        
        self.assertEqual(len(dependencies), 2, "Test job should have two upstream dependencies")
        names = []
        names.append(dependencies[0].name)
        names.append(dependencies[1].name)
        self.assertTrue(upstream_job_name1 in names, "Mock job #1 should be returned as a direct dependency")
        self.assertTrue(upstream_job_name2 in names, "Mock job #2 should be returned as a direct dependency")
       
    def test_multiple_upstream_jobs_recursive(self):
        
        # job j1 has no upstream dependencies
        upstream_job_name1 = "j1"
        upstream_job_url1 = "http://localhost:8080/job/" + upstream_job_name1
        mock_job1_data_io = MagicMock()
        mock_job1_data_io.get_api_data.return_value = {"name": upstream_job_name1, "upstreamProjects": []}
        mock_job1_data_io.config_xml = "<project></project>"

        # job j1 triggers job j2
        upstream_job_name2 = "j2"
        upstream_job_url2 = "http://localhost:8080/job/" + upstream_job_name2 
        mock_job2_data_io = MagicMock()
        mock_job2_data_io.get_api_data.return_value = {"name": upstream_job_name2, "upstreamProjects": [{"url": upstream_job_url1}]}
        mock_job2_data_io.clone.return_value = mock_job1_data_io
        mock_job2_data_io.config_xml = "<project></project>"

        # job j3 triggers job j2
        upstream_job_name3 = "j3"
        upstream_job_url3 = "http://localhost:8080/job/" + upstream_job_name3
        mock_job3_data_io = MagicMock()
        mock_job3_data_io.get_api_data.return_value = {"name": upstream_job_name3, "upstreamProjects": [{"url": upstream_job_url2}]}
        mock_job3_data_io.clone.return_value = mock_job2_data_io
        mock_job3_data_io.config_xml = "<project></project>"

        # job j2 triggers our main job
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"upstreamProjects": [{"url": upstream_job_url3}]}
        mock_data_io.clone.return_value = mock_job3_data_io
        mock_data_io.config_xml = "<project></project>"

        # code under test 
        j = vJob(mock_data_io, None)
        dependencies = j.all_upstream_jobs
        
        # validation
        self.assertEqual(len(dependencies), 3, "Test job should have three upstream dependencies")
        names = []
        names.append(dependencies[0].name)
        names.append(dependencies[1].name)
        names.append(dependencies[2].name)
        self.assertTrue(upstream_job_name1 in names, "Mock job #1 should be returned as a transient dependency")
        self.assertTrue(upstream_job_name2 in names, "Mock job #2 should be returned as a transient dependency")
        self.assertTrue(upstream_job_name3 in names, "Mock job #3 should be returned as a direct dependency")

@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
class job_build_methods_tests(unittest.TestCase):
    """Tests for build related methods exposed by the 'Job' API"""
    def test_get_no_recent_builds(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"builds":[]}
 
        j = vJob (mock_data_io, None)
        builds = j.recent_builds
        
        self.assertEqual(len(builds), 0, "Job object should not contain any valid builds")
        
    def test_get_one_recent_build(self):
        expected_build_number = 123
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"builds":[{"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
        j = vJob (mock_data_io, None)
        builds = j.recent_builds
        
        self.assertEqual(len(builds), 1, "Job should have returned a single build")
        self.assertEqual(builds[0].number, expected_build_number)
        
    def test_get_last_good_build_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastSuccessfulBuild": None}
        
        j = vJob(mock_data_io, None)

        self.assertEqual(j.last_good_build, None)
        
    def test_get_last_good_build(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastSuccessfulBuild": {"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}}
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.last_good_build
        
        self.assertEqual(b.number, expected_build_number)
        
    def test_get_last_build_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastBuild": None}
        
        j = vJob(mock_data_io, None)

        self.assertEqual(j.last_build, None)
        
    def test_get_last_build(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastBuild": {"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}}
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.last_build
        
        self.assertEqual(b.number, expected_build_number)

    def test_get_last_failed_build_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastFailedBuild": None}
        
        j = vJob(mock_data_io, None)

        self.assertEqual(j.last_failed_build, None)
        
    def test_get_last_failed_build(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastFailedBuild": {"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}}
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.last_failed_build
        
        self.assertEqual(b.number, expected_build_number)
    
    def test_get_last_stable_build_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastCompletedBuild": None}
        
        j = vJob(mock_data_io, None)

        self.assertEqual(j.last_stable_build, None)
        
    def test_get_last_stable_build(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastCompletedBuild": {"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}}
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.last_stable_build
        
        self.assertEqual(b.number, expected_build_number)
        
    def test_get_last_unsuccessful_build_none(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastUnsuccessfulBuild": None}
        
        j = vJob(mock_data_io, None)

        self.assertEqual(j.last_unsuccessful_build, None)
        
    def test_get_last_unsuccessful_build(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"lastUnsuccessfulBuild": {"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}}
        mock_data_io.clone.return_value = build_mock_data_io

        j = vJob(mock_data_io, None)
        b = j.last_unsuccessful_build
        
        self.assertEqual(b.number, expected_build_number)
        
    def test_get_build_by_number(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        build_mock_data_io.get_api_data.return_value = {"number": expected_build_number}
        
        mock_data_io = MagicMock()
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.get_build_by_number(expected_build_number)
        
        self.assertEqual(b.number, expected_build_number)
        
    def test_get_build_by_number_non_existent(self):
        expected_build_number = 123
        build_mock_data_io = MagicMock()
        # The pyjen.Job API should be checking for an AssertionError to get
        # thrown by the dataio object when checking for the existence of a
        # given build
        build_mock_data_io.get_api_data.side_effect = AssertionError()
        
        mock_data_io = MagicMock()
        mock_data_io.clone.return_value = build_mock_data_io
        
        j = vJob(mock_data_io, None)
        b = j.get_build_by_number(expected_build_number)
        
        self.assertEqual(b, None, "Attempting to load a non existent build by numeric value should return None")
        
    def test_get_builds_in_time_range_no_builds(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[]}
 
        start_time = datetime(2013, 1, 21, 12, 0, 0)
        end_time = datetime(2013, 1, 21, 13, 0, 0)        
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(start_time, end_time)
        
        self.assertEqual(len(builds), 0, "Job object should not find any builds for the given time frame")
        
    def test_get_builds_in_time_range_no_builds_in_range(self):
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":123, "timestamp":0}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[{"url":"http://localhost:8080/job/j1/123"}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
 
        start_time = datetime(2013, 1, 21, 12, 0, 0)
        end_time = datetime(2013, 1, 21, 13, 0, 0)        
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(start_time, end_time)
        
        self.assertEqual(len(builds), 0, "Job object should not find any builds for the given time frame")
    
    def test_get_builds_in_time_range_one_match(self):
        expected_build_number = 123
        import time
        from datetime import datetime
        epoch_time = time.time()

        # Jenkins timestamps are stored in milliseconds
        time_in_milliseconds = epoch_time * 1000
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":expected_build_number, "timestamp":time_in_milliseconds}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[{"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}]}
        mock_data_io.clone.return_value = mock_build1_data_io

        start_time = datetime.fromtimestamp(epoch_time - 1000)
        end_time = datetime.fromtimestamp(epoch_time + 1000)
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(start_time, end_time)
        
        self.assertEqual(len(builds), 1, "One job should have been successfully detected for the given time interval")    
        self.assertEqual(builds[0].number, expected_build_number)
        
    def test_get_builds_in_time_range_inverted_parameters(self):
        expected_build_number = 123
        import time
        from datetime import datetime
        epoch_time = time.time()

        # Jenkins timestamps are stored in milliseconds
        time_in_milliseconds = epoch_time * 1000
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":expected_build_number, "timestamp":time_in_milliseconds}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[{"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
 
        start_time = datetime.fromtimestamp(epoch_time + 1000)
        end_time = datetime.fromtimestamp(epoch_time - 1000)
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(end_time, start_time)
        
        self.assertEqual(len(builds), 1, "One job should have been successfully detected for the given time interval")    
        self.assertEqual(builds[0].number, expected_build_number)
        
    def test_get_builds_in_time_range_lower_bound(self):
        import time
        from datetime import datetime
        epoch_time = time.time()

        # Jenkins timestamps are stored in milliseconds
        start_time_in_milliseconds = epoch_time * 1000

        start_time = datetime.fromtimestamp(epoch_time)
        end_time = datetime.fromtimestamp(epoch_time + 1000)

        expected_build_number = 123
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":expected_build_number, "timestamp":start_time_in_milliseconds}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[{"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
 
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(start_time, end_time)
        
        self.assertEqual(len(builds), 1, "One job should have been successfully detected for the given time interval")    
        self.assertEqual(builds[0].number, expected_build_number)
        
    def test_get_builds_in_time_range_upper_bound(self):
        import time
        from datetime import datetime
        epoch_time = time.time()

        # Jenkins timestamps are stored in milliseconds
        end_time_in_milliseconds = epoch_time * 1000

        start_time = datetime.fromtimestamp(epoch_time - 1000)
        end_time = datetime.fromtimestamp(epoch_time)
        expected_build_number = 123
        mock_build1_data_io = MagicMock()
        mock_build1_data_io.get_api_data.return_value = {"number":expected_build_number, "timestamp":end_time_in_milliseconds}
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"allBuilds":[{"url":"http://localhost:8080/job/j1/" + str(expected_build_number)}]}
        mock_data_io.clone.return_value = mock_build1_data_io
        
 
        j = vJob (mock_data_io, None)
        builds = j.get_builds_in_time_range(start_time, end_time)
        
        self.assertEqual(len(builds), 1, "One job should have been successfully detected for the given time interval")    
        self.assertEqual(builds[0].number, expected_build_number)
        
    
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
