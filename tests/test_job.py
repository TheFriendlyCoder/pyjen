from pyjen.job import Job
from pyjen.build import Build
from mock import MagicMock
import pytest
from datetime import datetime
import time
import xml.etree.ElementTree as ElementTree
from pyjen.jenkins import Jenkins
from pyjen.plugins.freestylejob import FreestyleJob


def test_create_freestyle_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_freestyle_job", "project")
    assert jb is not None
    jb.delete()


def test_find_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_find_job"
    jb1 = jk.create_job(expected_name, "project")
    try:
        assert jb1 is not None
        jb2 = jk.find_job(expected_name)
        assert jb2 is not None
        assert jb2.name == expected_name
        assert jb2.url == jb1.url
    finally:
        jb1.delete()


def test_derived_job_object(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_derived_job_object"
    jb1 = jk.create_job(expected_name, "project")
    try:
        assert jb1 is not None
        jb2 = jk.find_job(expected_name)
        assert jb2 is not None
        assert jb2.name == expected_name
        assert jb2.url == jb1.url

        derived = jb2.derived_object

        assert isinstance(derived, FreestyleJob)
    finally:
        jb1.delete()


def test_delete_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_delete_job"
    jb = jk.create_job(expected_name, "project")
    jb.delete()
    res = jk.find_job(expected_name)
    assert res is None


def test_get_job_name(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_get_job_name"
    jb = jk.create_job(expected_name, "project")
    try:
        assert jb.name == expected_name
    finally:
        jb.delete()


def test_is_disabled_defaults(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_is_disabled_defaults", "project")
    try:
        assert not jb.is_disabled
    finally:
        jb.delete()


def test_disable(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_disable", "project")
    try:
        jb.disable()
        assert jb.is_disabled
    finally:
        jb.delete()


def test_enable(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_enable", "project")
    try:
        jb.disable()
        jb.enable()
        assert not jb.is_disabled
    finally:
        jb.delete()


def test_has_not_been_built(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_has_not_been_built", "project")
    try:
        assert not jb.has_been_built
    finally:
        jb.delete()


def test_get_config_xml(jenkins_env):

    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_config_xml", "project")
    try:
        res = jb.config_xml
        assert res is not None
        xml = ElementTree.fromstring(res)
        assert xml.tag == "project"
    finally:
        jb.delete()


def test_clone(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_master", "project")
    jb_clone = None
    try:
        expected_name = "test_clone_second"
        jb_clone = jb.clone(expected_name)
        assert jb_clone is not None
        assert jb_clone.name == expected_name
        assert jb_clone.is_disabled
    finally:
        jb.delete()
        if jb_clone:
            jb_clone.delete()


def test_no_downstream_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_no_downstream_jobs", "project")
    try:
        dependencies = jb.downstream_jobs

        assert isinstance(dependencies, list)
        assert len(dependencies) == 0
    finally:
        jb.delete()


def test_no_upstream_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_no_upstream_jobs", "project")
    try:
        dependencies = jb.upstream_jobs

        assert isinstance(dependencies, list)
        assert len(dependencies) == 0
    finally:
        jb.delete()


def test_get_no_recent_builds(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_no_recent_builds", "project")
    try:
        builds = jb.recent_builds

        assert isinstance(builds, list)
        assert len(builds) == 0
    finally:
        jb.delete()


def test_start_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_start_build", "project")
    try:
        jb.start_build()
    finally:
        jb.delete()


def test_get_last_good_build_none(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_good_build_none", "project")
    try:
        bld = jb.last_good_build

        assert bld is None
    finally:
        jb.delete()


def test_get_last_build_none(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_build_none", "project")
    try:
        bld = jb.last_build

        assert bld is None
    finally:
        jb.delete()


def test_get_last_failed_build_none(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_failed_build_none", "project")
    try:
        bld = jb.last_failed_build

        assert bld is None
    finally:
        jb.delete()


def test_get_last_stable_build_none(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_stable_build_none", "project")
    try:
        bld = jb.last_stable_build

        assert bld is None
    finally:
        jb.delete()


def test_get_last_unsuccessful_build_none(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_unsuccessful_build_none", "project")
    try:
        bld = jb.last_unsuccessful_build

        assert bld is None
    finally:
        jb.delete()


def test_get_build_by_number_non_existent(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_build_by_number_non_existent", "project")
    try:
        bld = jb.get_build_by_number(1024)

        assert bld is None
    finally:
        jb.delete()


def test_no_build_health(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_no_build_health", "project")
    try:
        score = jb.build_health
        assert score == 0
    finally:
        jb.delete()


def test_has_been_built(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_has_been_built", "project")
    try:
        jb.start_build()
        # TODO: Find a way to reliably detect when a build is complete
        time.sleep(10)
        assert jb.has_been_built
    finally:
        jb.delete()


def test_build_health(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_build_health", "project")
    try:
        jb.start_build()
        # TODO: Find a way to reliably detect when a build is complete
        time.sleep(10)
        assert jb.has_been_built
        score = jb.build_health
        assert score == 100
    finally:
        jb.delete()

# TODO: add support for publishers to API so we can test upstream/downstream jobs
# def test_publishers(jenkins_env):
#     jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
#     jb = jk.find_job("third")
#     for cur_pub in jb.publishers:
#         print(cur_pub)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#       LEGACY TESTS
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


def test_get_one_recent_build(monkeypatch):
    build_url = "http://localhost:8080/job/MyJob1/123"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('builds', [{"url": build_url}]))

    j = Job("http://localhost:8080/job/MyJob1")
    builds = j.recent_builds

    assert len(builds) == 1
    assert isinstance(builds[0], Build)
    assert builds[0].url == build_url + "/"     # The API should append a trailing slash to our URL


def test_get_last_good_build(monkeypatch):
    build_url = "http://localhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastSuccessfulBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_good_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_failed_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastFailedBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_failed_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


def test_get_last_stable_build(monkeypatch):
    build_url = "http://localhhost:8080/job/MyJob1/99/"
    monkeypatch.setattr(Job, "get_api_data", get_mock_api_data('lastCompletedBuild', {"url": build_url}))

    j = Job("http://localhost:8080/job/MyJob1")
    bld = j.last_stable_build

    assert isinstance(bld, Build)
    assert bld.url == build_url


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


@pytest.mark.skip("Intermittently failing test")
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


@pytest.mark.skip("Intermittently failing test")
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





if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
