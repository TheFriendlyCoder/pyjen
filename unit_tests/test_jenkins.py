from pyjen.jenkins import Jenkins
from mock import MagicMock
import pytest
from mock import PropertyMock
from pytest import raises
from pyjen.job import Job
from pyjen.view import View
from pyjen.exceptions import PluginNotSupportedError
from pyjen.utils.jenkins_api import JenkinsAPI


fake_jenkins_url = "http://localhost:8080/"
fake_default_view_name = "MyPrimaryView"
fake_default_view_url = fake_jenkins_url + "view/" + fake_default_view_name + "/"
fake_second_view_name = "MySecondView"
fake_second_view_url = fake_jenkins_url + "view/" + fake_second_view_name + "/"

fake_jenkins_data = {
    "quietingDown": True,
    "jobs": [],
    "primaryView": {
        "name": fake_default_view_name,
        "url": fake_jenkins_url
    },
    "views": [
        {"name": fake_default_view_name, "url": fake_jenkins_url},
        {"name": fake_second_view_name, "url": fake_second_view_url}
    ]
}

fake_jenkins_headers = {
    "x-jenkins": "2.0.0"
}

@pytest.fixture
def patch_jenkins_api(monkeypatch):
    mock_api_data = MagicMock()
    mock_api_data.return_value = fake_jenkins_data
    monkeypatch.setattr(Jenkins, "get_api_data", mock_api_data)

    mock_headers = PropertyMock()
    mock_headers.return_value = fake_jenkins_headers
    monkeypatch.setattr(Jenkins, "jenkins_headers", mock_headers)


def get_mock_api_data(field, data):
    tmp_data = fake_jenkins_data.copy()
    tmp_data[field] = data
    mock_api_data = MagicMock()
    mock_api_data.return_value = tmp_data
    return mock_api_data


def test_init():
    jenkins_url = "http://localhost:8080"
    jenkins_user = "MyUser"
    jenkins_pw = "MyPass"
    jenkins_creds = (jenkins_user, jenkins_pw)
    j = Jenkins(jenkins_url, jenkins_creds, True)

    assert j.url == jenkins_url + "/"       # The API should append a slash to the URL for consistency

    # Constructor should initialize our global state as well
    assert JenkinsAPI.creds == jenkins_creds
    assert JenkinsAPI.jenkins_root_url == j.url
    assert JenkinsAPI.ssl_verify_enabled is True


def test_get_version(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")

    assert j.version == (2, 0, 0)


def test_get_unknown_version(monkeypatch):
    from requests.exceptions import InvalidHeader
    mock_header = PropertyMock()
    mock_header.return_value = {}   # no version info in the header
    monkeypatch.setattr(Jenkins, "jenkins_headers", mock_header)
    j = Jenkins("http://localhost:8080")

    with raises(InvalidHeader):
        j.version


def test_prepare_shutdown(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Jenkins, "post", mock_post)

    jenkins_url = "http://localhost:8080"
    j = Jenkins(jenkins_url)
    j.prepare_shutdown()

    mock_post.assert_called_once_with(jenkins_url + "/quietDown")


def test_cancel_shutdown(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Jenkins, "post", mock_post)

    jenkins_url = "http://localhost:8080"
    j = Jenkins(jenkins_url)
    j.cancel_shutdown()

    mock_post.assert_called_once_with(jenkins_url + "/cancelQuietDown")


def test_is_shutting_down(patch_jenkins_api):

    j = Jenkins("http://localhost:8080")
    assert j.is_shutting_down is True


def test_find_non_existent_job(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    jb = j.find_job("DoesNotExistJob")
    assert jb is None


def test_find_job(monkeypatch):
    expected_job_name = "MyJob"
    expected_job_url = "http://localhost:8080/job/MyJob/"
    fake_jobs = [
        {"name": "AnotherJob", "url": "http://localhost:8080/job/AnotherJob"},
        {"name": expected_job_name, "url": expected_job_url}
    ]
    monkeypatch.setattr(Jenkins, "get_api_data", get_mock_api_data("jobs", fake_jobs))

    j = Jenkins("http://localhost:8080")
    jb = j.find_job("MyJob")

    assert isinstance(jb, Job)
    assert jb.url == expected_job_url


def test_create_job(monkeypatch):
    expected_name = "MyJob2"
    expected_url = "http://localhost:8080/job/MyJob2/"

    mock_post = MagicMock()
    monkeypatch.setattr(Jenkins, "post", mock_post)

    j = Jenkins("http://localhost:8080")
    jb = j.create_job(expected_name, "project")

    assert isinstance(jb, Job)
    assert jb.url == expected_url
    assert mock_post.call_count == 1


def test_create_unsupported_job_type(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Jenkins, "post", mock_post)

    j = Jenkins("http://localhost:8080")
    with raises(PluginNotSupportedError):
        jb = j.create_job("SomeNewJob", "FuBarType")


def test_get_default_view(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    v = j.default_view

    assert v.url == fake_jenkins_url + "view/" + fake_default_view_name + "/"


def test_get_multiple_views(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    views = j.views

    assert len(views) == 2
    for cur_view in views:
        assert cur_view.url in [fake_second_view_url, fake_default_view_url]
    assert views[0].url != views[1].url


def test_find_view(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    v = j.find_view(fake_second_view_name)

    assert isinstance(v, View)
    assert v.url == fake_second_view_url


def test_find_missing_view(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    v = j.find_view("DoesNotExist")

    assert v is None


def test_find_view_primary_view(patch_jenkins_api):
    j = Jenkins("http://localhost:8080")
    v = j.find_view(fake_default_view_name)

    assert isinstance(v, View)
    assert v.url == fake_default_view_url


def test_create_view(monkeypatch):
    new_view_name = "MyNewView"
    expected_view_url = fake_jenkins_url + "view/" + new_view_name + "/"
    expected_view_type = "ListView"
    mock_post = MagicMock()
    monkeypatch.setattr(Jenkins, "post", mock_post)
    monkeypatch.setattr(Jenkins, "get_api_data", get_mock_api_data("views", [{"name": new_view_name, "url": expected_view_url}]))
    j = Jenkins(fake_jenkins_url)
    v = j.create_view(new_view_name, expected_view_type)

    assert isinstance(v, View)
    assert v.url == expected_view_url
    assert mock_post.call_count == 1
    assert mock_post.call_args[0][0] == fake_jenkins_url + "createView"
    assert mock_post.call_args[0][1]['data']['name'] == new_view_name
    assert mock_post.call_args[0][1]['data']['mode'] == expected_view_type


def test_get_multiple_nodes(monkeypatch):
    mock_api_data = MagicMock()
    fake_node1_url = fake_jenkins_url + "computer/(master)/"
    fake_node2_url = fake_jenkins_url + "computer/remoteNode1/"

    fake_api_data = {
        "computer": [
            {"displayName": "master"},
            {"displayName": "remoteNode1"}
        ]
    }
    mock_api_data.return_value = fake_api_data
    monkeypatch.setattr(Jenkins, "get_api_data", mock_api_data)

    j = Jenkins("http://localhost:8080")
    nodes = j.nodes

    assert len(nodes) == 2
    for cur_node in nodes:
        assert cur_node.url in [fake_node1_url, fake_node2_url]
    assert nodes[0].url != nodes[1].url

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
