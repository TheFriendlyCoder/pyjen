from pyjen.jenkins import Jenkins
from mock import MagicMock, patch
import pytest
from .utils import clean_view, clean_job, async_assert
from pyjen.plugins.shellbuilder import ShellBuilder


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
    assert v.name == "all"


def test_get_views(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.views

    assert v is not None
    assert isinstance(v, list)
    assert len(v) == 1
    assert v[0].name == "all"


def test_get_multiple_views(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    test_view_name = "test_get_multiple_views_view"
    vw = jk.create_view(test_view_name, "hudson.model.ListView")
    with clean_view(vw):
        v = jk.views

        assert v is not None
        assert isinstance(v, list)
        assert len(v) == 2
        assert v[0].name in ["all", test_view_name]
        assert v[1].name in ["all", test_view_name]
        assert v[0].name != v[1].name


def test_find_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "all"
    v = jk.find_view(expected_name)

    assert v is not None
    assert v.name == expected_name


def test_create_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    vw = jk.create_view("test_create_view", "hudson.model.ListView")
    with clean_view(vw):
        assert vw is not None
        assert vw.name == "test_create_view"


def test_clone_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    vw = jk.create_view("test_clone_view1", "hudson.model.ListView")
    with clean_view(vw):
        expected_name = "test_clone_view2"
        vw2 = jk.clone_view(vw, expected_name)
        assert vw2 is not None
        with clean_view(vw2):
            assert vw2.name == expected_name
            assert isinstance(vw2, type(vw))


def test_rename_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    view_name_1 = "test_clone_view1"
    vw = jk.create_view(view_name_1, "hudson.model.ListView")
    try:
        expected_name = "test_clone_view2"
        vw2 = jk.rename_view(vw.name, expected_name)
        assert vw2 is not None
        with clean_view(vw2):
            tmp_view = jk.find_view(expected_name)
            assert tmp_view is not None
            assert tmp_view.name == expected_name
            assert isinstance(vw2, type(vw))
            assert jk.find_view(view_name_1) is None
    except:
        tmp = jk.find_view(view_name_1)
        if tmp:
            tmp.delete()
        raise


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


def test_create_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_job", "hudson.model.FreeStyleProject")
    with clean_job(jb):
        assert jb is not None


def test_clone_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job", "hudson.model.FreeStyleProject")
    with clean_job(jb):
        # add a builder to our source job so we can check to make sure the
        # configuration has been properly cloned
        expected_script = "echo Hello From TestCloneJob"
        failing_step = ShellBuilder.create(expected_script)
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        # now, clone our job configuration and make sure the entire config
        # has been cloned correctly
        expected_name = "test_clone_job2"
        jb_clone = jk.clone_job(jb, expected_name)
        with clean_job(jb_clone):
            assert jb_clone is not None
            assert jb_clone.name == expected_name
            assert jb_clone.is_disabled
            results = jb_clone.builders
            assert results is not None
            assert isinstance(results, list)
            assert len(results) == 1
            assert isinstance(results[0], ShellBuilder)
            assert results[0].script == expected_script


def test_clone_job_enabled(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job_enabled", "hudson.model.FreeStyleProject")
    with clean_job(jb):
        jb_clone = jk.clone_job(jb, "test_clone_job2", False)
        with clean_job(jb_clone):
            assert jb_clone is not None
            assert jb_clone.is_disabled is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
