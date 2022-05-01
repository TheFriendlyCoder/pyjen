from pyjen.jenkins import Jenkins
from mock import MagicMock
from .utils import clean_view, clean_job
from pyjen.plugins.listview import ListView
from pyjen.plugins.freestylejob import FreestyleJob
from pyjen.plugins.folderjob import FolderJob


def test_simple_connection(jenkins_api):
    assert jenkins_api.connected


def test_not_connected():
    jk = Jenkins.basic_auth("https://0.0.0.0")
    assert not jk.connected


def test_failed_connection_check():

    mock_response = MagicMock()
    mock_response.headers = None
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    jk = Jenkins("https://0.0.0.0", mock_session)
    assert not jk.connected

    mock_session.get.assert_called_once()


def test_get_version(jenkins_api):
    assert jenkins_api.version
    assert isinstance(jenkins_api.version, tuple)


def test_is_shutting_down(jenkins_api):
    assert not jenkins_api.is_shutting_down


def test_cancel_shutdown_not_quietdown_mode(jenkins_api):
    assert not jenkins_api.is_shutting_down
    jenkins_api.cancel_shutdown()
    assert not jenkins_api.is_shutting_down


def test_cancel_shutdown(jenkins_api):
    try:
        jenkins_api.prepare_shutdown()
        assert jenkins_api.is_shutting_down
        jenkins_api.cancel_shutdown()
        assert not jenkins_api.is_shutting_down
    finally:
        jenkins_api.cancel_shutdown()


def test_prepare_shutdown(jenkins_api):
    try:
        jenkins_api.prepare_shutdown()
        assert jenkins_api.is_shutting_down
    finally:
        jenkins_api.cancel_shutdown()


def test_find_non_existent_job(jenkins_api):
    jb = jenkins_api.find_job("DoesNotExistJob")
    assert jb is None


def test_get_default_view(jenkins_api):
    v = jenkins_api.default_view
    assert v is not None
    assert v.name == "all"


def test_get_views(jenkins_api):
    v = jenkins_api.views

    assert v is not None
    assert isinstance(v, list)
    assert len(v) == 1
    assert v[0].name == "all"


def test_get_multiple_views(jenkins_api):
    test_view_name = "test_get_multiple_views_view"
    vw = jenkins_api.create_view(test_view_name, ListView)
    with clean_view(vw):
        v = jenkins_api.views

        assert v is not None
        assert isinstance(v, list)
        assert len(v) == 2
        assert v[0].name in ["all", test_view_name]
        assert v[1].name in ["all", test_view_name]
        assert v[0].name != v[1].name


def test_find_view(jenkins_api):
    expected_name = "all"
    v = jenkins_api.find_view(expected_name)

    assert v is not None
    assert v.name == expected_name


def test_create_view(jenkins_api):
    vw = jenkins_api.create_view("test_create_view", ListView)
    with clean_view(vw):
        assert vw is not None
        assert vw.name == "test_create_view"


def test_find_missing_view(jenkins_api):
    v = jenkins_api.find_view("DoesNotExist")

    assert v is None


def test_get_nodes(jenkins_api):
    nodes = jenkins_api.nodes

    assert nodes is not None
    assert isinstance(nodes, list)
    assert len(nodes) == 1
    assert nodes[0].name == "Built-In Node"


def test_find_node(jenkins_api):
    node = jenkins_api.find_node("Built-In Node")

    assert node is not None
    assert node.name == "Built-In Node"


def test_find_node_not_exists(jenkins_api):
    node = jenkins_api.find_node("NodeDoesNotExist")

    assert node is None


def test_find_user(jenkins_env, jenkins_api):
    user = jenkins_api.find_user(jenkins_env["admin_user"])
    assert user is not None
    assert user.full_name == jenkins_env["admin_user"]


def test_find_user_not_exists(jenkins_api):
    user = jenkins_api.find_user("UserDoesNotExist")
    assert user is None


def test_get_plugin_manager(jenkins_api):
    pm = jenkins_api.plugin_manager

    assert pm is not None


def test_get_no_jobs(jenkins_api):
    res = jenkins_api.jobs

    assert res is not None
    assert isinstance(res, list)
    assert len(res) == 0


def test_get_one_job(jenkins_api):
    jb = jenkins_api.create_job("test_get_one_job", FreestyleJob)
    with clean_job(jb):
        res = jenkins_api.jobs

        assert len(res) == 1
        assert res[0] == jb


def test_get_no_jobs_recursive(jenkins_api):
    res = jenkins_api.all_jobs

    assert res is not None
    assert isinstance(res, list)
    assert len(res) == 0


def test_get_one_job_recursive(jenkins_api):
    jb1 = jenkins_api.create_job("test_get_one_job_recursive_1", FolderJob)
    with clean_job(jb1):
        jb2 = jb1.create_job("test_get_one_job_recursive_2", FreestyleJob)
        with clean_job(jb2):
            assert len(jenkins_api.all_jobs) > len(jenkins_api.jobs)
            res = jenkins_api.all_jobs
            assert len(res) == 2
            assert jb1 in res
            assert jb2 in res


def test_get_multi_nested_job_recursive(jenkins_api):
    jb1 = jenkins_api.create_job("test_get_multi_nested_job_recursive_1", FolderJob)
    with clean_job(jb1):
        jb2 = jb1.create_job("test_get_multi_nested_job_recursive_2", FreestyleJob)
        with clean_job(jb2):
            jb3 = jb1.create_job("test_get_multi_nested_job_recursive_3", FolderJob)
            with clean_job(jb3):
                jb4 = jb3.create_job("test_get_multi_nested_job_recursive_4", FreestyleJob)
                with clean_job(jb4):
                    res = jenkins_api.all_jobs
                    assert len(res) == 4
                    assert jb1 in res
                    assert jb2 in res
                    assert jb3 in res
                    assert jb4 in res


def test_create_job(jenkins_api):
    jb = jenkins_api.create_job("test_create_job", FreestyleJob)
    with clean_job(jb):
        assert jb is not None


def test_build_queue(jenkins_api):
    queue = jenkins_api.build_queue
    assert queue is not None
    assert isinstance(queue.items, list)
    assert len(queue.items) == 0
