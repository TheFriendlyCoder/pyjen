import unittest
from pyjen.job import Job
from mock import MagicMock
import pytest
from datetime import datetime

# This dictionary represents a "typical" dataset returned by the Jenkins REST API
# when querying information about a job. This is used to fake output from the REST API
# for tests below.

fake_job_data = {
    "name": "MyJob1",
    "color": "blue",
    "downstreamProjects": [],   # no downstream jobs
    "upstreamProjects": []      # no upstream jobs
}

@pytest.fixture
def patch_job_api(monkeypatch):
    monkeypatch.setattr(Job, "get_api_data", lambda s: fake_job_data)


def test_get_name(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    assert j.name == fake_job_data["name"]


def test_start_build(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    j.start_build()

    mock_post.assert_called_once_with(job_url + "/build")


def test_disable(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    j.disable()

    mock_post.assert_called_once_with(job_url + "/disable")


def test_enable(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    j.enable()

    mock_post.assert_called_once_with(job_url + "/enable")


def test_is_enabled(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    assert j.is_disabled is False


def test_is_disabled(monkeypatch):
    tmp_data = fake_job_data.copy()
    tmp_data["color"] = "disabled"
    monkeypatch.setattr(Job, "get_api_data", lambda s: tmp_data)

    j = Job("http://localhost:8080/job/MyJob1")
    assert j.is_disabled is True


def test_delete(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    j.delete()

    mock_post.assert_called_once_with(job_url + "/doDelete")


def test_has_not_been_built(monkeypatch):
    tmp_data = fake_job_data.copy()
    tmp_data["color"] = "notbuilt"
    monkeypatch.setattr(Job, "get_api_data", lambda s: tmp_data)

    j = Job("http://localhost:8080/job/MyJob1")
    assert j.has_been_built is False


def test_has_been_built(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    assert j.has_been_built is True


def test_get_config_xml(monkeypatch):
    expected_config_xml = "<Sample Config XML/>"
    mock_get_text = MagicMock()
    mock_get_text.return_value = expected_config_xml
    monkeypatch.setattr(Job, "get_text", mock_get_text)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)

    assert j.config_xml == expected_config_xml
    mock_get_text.assert_called_once_with("/config.xml")


def test_set_config_xml(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)

    expected_config_xml = "<Sample Config XML/>"

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    j.config_xml = expected_config_xml

    # Make sure our post operation was structured as expected
    assert mock_post.call_count == 1
    assert len(mock_post.call_args) == 2
    assert mock_post.call_args[0][0] == job_url + "/config.xml"
    assert 'data' in mock_post.call_args[0][1]
    assert mock_post.call_args[0][1]['data'] == expected_config_xml


def test_clone(monkeypatch):
    new_job_name = "MyNewJob"
    mock_post = MagicMock()
    monkeypatch.setattr(Job, "post", mock_post)
    monkeypatch.setattr(Job, "get_api_data", lambda s: fake_job_data)

    jenkins_url = "http://localhost:8080"
    j = Job(jenkins_url + "/job/MyJob1")
    newjob = j.clone(new_job_name)

    # Make sure our resulting object is of the correct type
    assert isinstance(newjob, Job)

    # Make sure our post calls have been correctly structured
    assert mock_post.call_count == 2
    first_call = mock_post.call_args_list[0]
    second_call = mock_post.call_args_list[1]

    # The first call should have been made to clone the job
    assert first_call[0][0] == jenkins_url + "/createItem"

    assert 'params' in first_call[0][1]
    assert 'name' in first_call[0][1]['params']
    assert first_call[0][1]['params']['name'] == new_job_name

    assert 'mode' in first_call[0][1]['params']
    assert first_call[0][1]['params']['mode'] == 'copy'

    assert 'from' in first_call[0][1]['params']
    assert first_call[0][1]['params']['from'] == fake_job_data['name']

    # The second call should have been made to disable the newly generated job
    assert second_call[0][0] == "http://localhost:8080/job/" + new_job_name + "/disable"


def test_supported_types():
    supported_types = Job.supported_types()

    assert "project" in supported_types
    assert len(supported_types) >= 1


def test_no_downstream_jobs(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.downstream_jobs

    assert len(dependencies) == 0


def test_one_downstream_job(monkeypatch):
    tmp_data = fake_job_data.copy()
    downstream_url = "http://localhost:8080/job/AnotherJob"
    tmp_data['downstreamProjects'] = [{"url": downstream_url}]
    monkeypatch.setattr(Job, "get_api_data", lambda s: tmp_data)

    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.downstream_jobs

    assert len(dependencies) == 1
    assert isinstance(dependencies[0], Job)
    assert dependencies[0].url == downstream_url + "/"   # the API should append a trailing slash to our URL


def test_multiple_downstream_jobs_recursive(monkeypatch):
    downstream_job1_url = "http://localhost:8080/job/Downstream1/"
    downstream_job2_url = "http://localhost:8080/job/Downstream2/"

    root_job = fake_job_data.copy()
    root_job['downstreamProjects'] = [{"url": downstream_job1_url}]

    downstream_job1 = fake_job_data.copy()
    downstream_job1['downstreamProjects'] = [{"url": downstream_job2_url}]

    downstream_job2 = fake_job_data.copy()  # our fake job has no downstreams so the cycle ends here

    mock_get_api_data = MagicMock()
    mock_get_api_data.side_effect = [root_job, downstream_job1, downstream_job2]

    monkeypatch.setattr(Job, "get_api_data", mock_get_api_data)

    # code under test
    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.all_downstream_jobs

    # validation
    assert len(dependencies) == 2
    for dep in dependencies:
        assert isinstance(dep, Job)
    assert dependencies[0].url == downstream_job1_url
    assert dependencies[1].url == downstream_job2_url


def test_no_upstream_jobs(patch_job_api):

    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.upstream_jobs

    assert len(dependencies) == 0


def test_one_upstream_job(monkeypatch):
    tmp_data = fake_job_data.copy()
    upstream_url = "http://localhost:8080/job/AnotherJob"
    tmp_data['upstreamProjects'] = [{"url": upstream_url}]
    monkeypatch.setattr(Job, "get_api_data", lambda s: tmp_data)

    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.upstream_jobs

    assert len(dependencies) == 1
    assert isinstance(dependencies[0], Job)
    assert dependencies[0].url == upstream_url + "/"   # the API should append a trailing slash to our URL


def test_multiple_upstream_jobs_recursive(monkeypatch):
    upstream_job1_url = "http://localhost:8080/job/Upstream1/"
    upstream_job2_url = "http://localhost:8080/job/Upstream2/"

    root_job = fake_job_data.copy()
    root_job['upstreamProjects'] = [{"url": upstream_job1_url}]

    upstream_job1 = fake_job_data.copy()
    upstream_job1['upstreamProjects'] = [{"url": upstream_job2_url}]

    upstream_job2 = fake_job_data.copy()  # our fake job has no upstreams so the cycle ends here

    mock_get_api_data = MagicMock()
    mock_get_api_data.side_effect = [root_job, upstream_job1, upstream_job2]

    monkeypatch.setattr(Job, "get_api_data", mock_get_api_data)

    # code under test
    j = Job("http://localhost:8080/job/MyJob1")
    dependencies = j.all_upstream_jobs

    # validation
    assert len(dependencies) == 2
    for dep in dependencies:
        assert isinstance(dep, Job)
    assert dependencies[0].url == upstream_job1_url
    assert dependencies[1].url == upstream_job2_url

class vJob(Job):
    type = ""


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