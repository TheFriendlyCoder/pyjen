from pyjen.job import Job
from pyjen.build import Build
from mock import MagicMock
import pytest
from datetime import datetime
import time

# This dictionary represents a "typical" dataset returned by the Jenkins REST API
# when querying information about a job. This is used to fake output from the REST API
# for tests below.
build_stability_score = 75
fake_job_data = {
    "name": "MyJob1",
    "color": "blue",
    "downstreamProjects": [],   # no downstream jobs
    "upstreamProjects": [],     # no upstream jobs
    "builds": [],               # no builds of the job
    "lastSuccessfulBuild": None,
    "lastBuild": None,
    "lastFailedBuild": None,
    "lastCompletedBuild": None,
    "lastUnsuccessfulBuild": None,
    "allBuilds": [],
    "healthReport": [{
        "description": "Build stability:",
        "score": build_stability_score
    }]
}

@pytest.fixture
def patch_job_api(monkeypatch):
    mock_api_data = MagicMock()
    mock_api_data.return_value = fake_job_data
    monkeypatch.setattr(Job, "get_api_data", mock_api_data)


def get_mock_api_data(field, data):
    tmp_data = fake_job_data.copy()
    tmp_data[field] = data
    mock_api_data = MagicMock()
    mock_api_data.return_value = tmp_data
    return mock_api_data




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


def test_get_no_recent_builds(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.recent_builds

    assert len(builds) == 0


def test_get_one_recent_build(monkeypatch):
    build_url = "http://localhost:8080/job/MyJob1/123"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('builds', [{"url": build_url}]))

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.recent_builds

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url + "/"     # The API should append a trailing slash to our URL


def test_get_last_good_build_none(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_good_build

    assert bld is None


def test_get_last_good_build(monkeypatch):
    build_url = "http://localhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastSuccessfulBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_good_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_build_none(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_build

    assert bld is None


def test_get_last_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_failed_build_none(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_failed_build

    assert bld is None


def test_get_last_failed_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastFailedBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_failed_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_stable_build_none(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_stable_build

    assert bld is None


def test_get_last_stable_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastCompletedBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_stable_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_unsuccessful_build_none(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_unsuccessful_build

    assert bld is None


def test_get_last_unsuccessful_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastUnsuccessfulBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_unsuccessful_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_build_by_number(monkeypatch):
    expected_build_number = 123
    tmp_data = {"number": expected_build_number}
    monkeypatch.setattr(Build, "get_api_data", lambda s: tmp_data)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    bld = j.get_build_by_number(expected_build_number)

    assert isinstance(bld, Build)
    assert bld.url == job_url + "/" + str(expected_build_number) + "/"


def test_get_build_by_number_non_existent(monkeypatch):
    expected_build_number = 123
    mock_api_data = MagicMock()
    mock_api_data.side_effect = AssertionError()
    monkeypatch.setattr(Build, "get_api_data", mock_api_data)

    job_url = "http://localhost:8080/job/MyJob1"
    j = Job(job_url)
    bld = j.get_build_by_number(expected_build_number)

    assert bld is None


def test_get_builds_in_time_range_no_builds(patch_job_api):
    start_time = datetime(2013, 1, 21, 12, 0, 0)
    end_time = datetime(2013, 1, 21, 13, 0, 0)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(start_time, end_time)

    assert len(builds) == 0


def test_get_builds_in_time_range_no_builds_in_range(monkeypatch):

    start_time = datetime(2013, 1, 21, 12, 0, 0)
    end_time = datetime(2013, 1, 21, 13, 0, 0)

    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data("allBuilds", [{"url": "http://localhost:8080/job/MyJob1/3"}]))
    mock_build_data = MagicMock()
    mock_build_data.return_value = {"timestamp": 1000}
    monkeypatch.setattr(Build, "get_api_data", mock_build_data)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(start_time, end_time)

    assert len(builds) == 0


def test_get_builds_in_time_range_one_match(monkeypatch):
    epoch_time = time.time()

    # Jenkins timestamps are stored in milliseconds
    time_in_milliseconds = epoch_time * 1000
    build_url = "http://localhost:8080/job/MyJob1/3/"
    monkeypatch.setattr(Job, "get_api_data",
                        get_mock_api_data("allBuilds", [{"url": build_url}]))
    mock_build_data = MagicMock()
    mock_build_data.return_value = {"timestamp": time_in_milliseconds}
    monkeypatch.setattr(Build, "get_api_data", mock_build_data)

    start_time = datetime.fromtimestamp(epoch_time - 1000)
    end_time = datetime.fromtimestamp(epoch_time + 1000)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(start_time, end_time)

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url


def test_get_builds_in_time_range_inverted_parameters(monkeypatch):
    epoch_time = time.time()

    # Jenkins timestamps are stored in milliseconds
    time_in_milliseconds = epoch_time * 1000
    build_url = "http://localhost:8080/job/MyJob1/3/"
    monkeypatch.setattr(Job, "get_api_data",
                        get_mock_api_data("allBuilds", [{"url": build_url}]))
    mock_build_data = MagicMock()
    mock_build_data.return_value = {"timestamp": time_in_milliseconds}
    monkeypatch.setattr(Build, "get_api_data", mock_build_data)

    start_time = datetime.fromtimestamp(epoch_time - 1000)
    end_time = datetime.fromtimestamp(epoch_time + 1000)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(end_time, start_time)

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url


def test_get_builds_in_time_range_lower_bound(monkeypatch):
    epoch_time = time.time()

    # Jenkins timestamps are stored in milliseconds
    time_in_milliseconds = epoch_time * 1000
    build_url = "http://localhost:8080/job/MyJob1/3/"
    monkeypatch.setattr(Job, "get_api_data",
                        get_mock_api_data("allBuilds", [{"url": build_url}]))
    mock_build_data = MagicMock()
    mock_build_data.return_value = {"timestamp": time_in_milliseconds}
    monkeypatch.setattr(Build, "get_api_data", mock_build_data)

    start_time = datetime.fromtimestamp(epoch_time)
    end_time = datetime.fromtimestamp(epoch_time + 10000)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(end_time, start_time)

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url


def test_get_builds_in_time_range_upper_bound(monkeypatch):
    epoch_time = time.time()

    # Jenkins timestamps are stored in milliseconds
    time_in_milliseconds = epoch_time * 1000
    build_url = "http://localhost:8080/job/MyJob1/3/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data("allBuilds", [{"url": build_url}]))
    mock_build_data = MagicMock()
    mock_build_data.return_value = {"timestamp": time_in_milliseconds}
    monkeypatch.setattr(Build, "get_api_data", mock_build_data)

    start_time = datetime.fromtimestamp(epoch_time - 10000)
    end_time = datetime.fromtimestamp(epoch_time)

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.get_builds_in_time_range(end_time, start_time)

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url


def test_build_health(patch_job_api):
    j = Job("http://localhost:8080/job/MyJob1")
    score = j.build_health

    assert score == build_stability_score


def test_no_build_health(monkeypatch):
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data("healthReport", []))

    j = Job("http://localhost:8080/job/MyJob1")
    score = j.build_health

    assert score == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])