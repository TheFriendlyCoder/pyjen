from pyjen.jenkins import Jenkins
from mock import MagicMock, PropertyMock, patch
import pytest
from pytest import raises
from pyjen.exceptions import PluginNotSupportedError


def test_simple_connection(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    assert jk.connected


def test_not_connected():
    jk = Jenkins("https://0.0.0.0")
    assert not jk.connected


def test_failed_connection_check():
    with patch("pyjen.utils.jenkins_api.requests") as req:
        mock_response = MagicMock()
        mock_response.headers = None
        req.get.return_value = mock_response

        jk = Jenkins("https://0.0.0.0")
        assert not jk.connected

        req.get.assert_called_once()


def test_get_version(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    assert jk.version
    assert isinstance(jk.version, tuple)


def test_is_shutting_down(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    assert not jk.is_shutting_down


def test_cancel_shutdown_not_quietdown_mode(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    assert not jk.is_shutting_down
    jk.cancel_shutdown()
    assert not jk.is_shutting_down


def test_cancel_shutdown(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    try:
        jk.prepare_shutdown()
        assert jk.is_shutting_down
        jk.cancel_shutdown()
        assert not jk.is_shutting_down
    finally:
        jk.cancel_shutdown()


def test_prepare_shutdown(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    try:
        jk.prepare_shutdown()
        assert jk.is_shutting_down
    finally:
        jk.cancel_shutdown()


def test_find_non_existent_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.find_job("DoesNotExistJob")
    assert jb is None


def test_get_default_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.default_view
    assert v is not None
    assert v.url.startswith(jenkins_env["url"])
    assert v.url == jenkins_env["url"] + "/view/all/"


def test_get_views(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.views

    assert v is not None
    assert isinstance(v, list)
    assert len(v) == 1
    assert v[0].name == "all"


def test_find_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.find_view("all")

    assert v is not None
    assert v.url == jenkins_env["url"] + "/view/all/"


def test_find_missing_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.find_view("DoesNotExist")

    assert v is None


def test_get_nodes(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    nodes = jk.nodes

    assert nodes is not None
    assert isinstance(nodes, list)
    assert len(nodes) == 1
    assert nodes[0].name == "master"


def test_find_node(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    node = jk.find_node("master")

    assert node is not None
    assert node.name == "master"


def test_find_node_not_exists(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    node = jk.find_node("NodeDoesNotExist")

    assert node is None


def test_find_user(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user(jenkins_env["admin_user"])
    assert user is not None
    assert user.full_name == jenkins_env["admin_user"]


def test_find_user_not_exists(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user("UserDoesNotExist")
    assert user is None


def test_get_plugin_manager(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    pm = jk.plugin_manager

    assert pm is not None


# TODO: Fix this test so coverage works correctly
# TODO: apply fix for pip install wheel file in my template project and elsewhere
# TODO: Find a way to get pycharm to preserve docker container
def test_get_plugin_template_not_supported():
    jk = Jenkins("http://0.0.0.0")
    with raises(PluginNotSupportedError):
        res = jk.get_plugin_template("DoesNotExistTemplate")
        assert res is None


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# legacy tests
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

def get_mock_api_data(field, data):
    tmp_data = fake_jenkins_data.copy()
    tmp_data[field] = data
    mock_api_data = MagicMock()
    mock_api_data.return_value = tmp_data
    return mock_api_data


def test_init():
    # THIS TEST SHOULD BE DEPRECATED AS SOON AS WE ELIMINATE GLOBAL STATE
    # FROM THE PYJEN API
    from pyjen.utils.jenkins_api import JenkinsAPI
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


def test_get_unknown_version(monkeypatch):
    from requests.exceptions import InvalidHeader
    mock_header = PropertyMock()
    mock_header.return_value = {}   # no version info in the header
    monkeypatch.setattr(Jenkins, "jenkins_headers", mock_header)
    j = Jenkins("http://localhost:8080")

    with raises(InvalidHeader):
        j.version


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

    assert jb.url == expected_job_url



if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
