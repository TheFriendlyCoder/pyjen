from mock import patch, MagicMock
from .utils import count_plugins
from pyjen.utils.plugin_api import find_plugin, get_all_plugins
from pyjen.view import View
from pyjen.job import Job


def test_unsupported_plugin(caplog):
    with patch("pyjen.utils.plugin_api.iter_entry_points") as entry_points:
        mock_plugin_class = MagicMock(spec=[])
        mock_ep = MagicMock()
        mock_ep.load.return_value = mock_plugin_class
        entry_points.return_value = [mock_ep]

        res = find_plugin("some_plugin")
        assert res is None
        assert "does not expose the required get_jenkins_plugin_name static method" in caplog.text


def test_one_supported_plugin(caplog):
    with patch("pyjen.utils.plugin_api.iter_entry_points") as entry_points:
        expected_plugin_name = "some_plugin"
        mock_plugin_class = MagicMock()
        mock_plugin_class.get_jenkins_plugin_name.return_value = expected_plugin_name

        mock_ep = MagicMock()
        mock_ep.load.return_value = mock_plugin_class

        entry_points.return_value = [mock_ep]

        res = find_plugin(expected_plugin_name)
        assert res is not None
        assert res == mock_plugin_class
        assert not caplog.text


def test_multiple_supported_plugin(caplog):
    with patch("pyjen.utils.plugin_api.iter_entry_points") as entry_points:
        expected_plugin_name = "some_plugin"
        mock_plugin_class1 = MagicMock()
        mock_plugin_class1.get_jenkins_plugin_name.return_value = expected_plugin_name

        mock_plugin_class2 = MagicMock()
        mock_plugin_class2.get_jenkins_plugin_name.return_value = expected_plugin_name

        mock_ep1 = MagicMock()
        mock_ep1.load.return_value = mock_plugin_class1
        mock_ep2 = MagicMock()
        mock_ep2.load.return_value = mock_plugin_class2

        entry_points.return_value = [mock_ep1, mock_ep2]

        res = find_plugin(expected_plugin_name)
        assert res is not None
        assert res == mock_plugin_class1
        assert "multiple plugins detected" in caplog.text


def test_list_plugins():
    res = get_all_plugins()
    assert res is not None
    assert isinstance(res, list)
    assert len(res) == count_plugins()


def test_load_all_job_plugins():
    plugins = Job.get_supported_plugins()
    assert plugins is not None
    assert isinstance(plugins, list)
    assert len(plugins) > 0

    mock_api = MagicMock()
    expected_name = "FakeName"
    mock_api.get_api_data.return_value = {
        "name": expected_name
    }
    for cur_plugin in plugins:
        job = cur_plugin(mock_api)
        assert job.name == expected_name
        assert isinstance(job, Job)


def test_load_all_view_plugins():
    plugins = View.get_supported_plugins()
    assert plugins is not None
    assert isinstance(plugins, list)
    assert len(plugins) > 0

    mock_api = MagicMock()
    expected_name = "FakeName"
    mock_api.get_api_data.return_value = {
        "name": expected_name
    }
    for cur_plugin in plugins:
        view = cur_plugin(mock_api)
        assert view.name == expected_name
        assert isinstance(view, View)
