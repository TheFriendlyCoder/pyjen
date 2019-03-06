import pytest
from mock import patch, MagicMock
from pyjen.utils.plugin_api import find_plugin
# import inspect
# from pyjen.utils.configxml import ConfigXML
# from .utils import count_plugins


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


# def test_list_plugins():
#     res = ConfigXML.get_installed_plugins()
#     assert res is not None
#     assert isinstance(res, list)
#     assert len(res) == count_plugins()
#
#
# def test_find_plugins():
#     plugin_names = ConfigXML.get_installed_plugins()
#     assert plugin_names
#
#     plugin = ConfigXML.find_plugin(plugin_names[0])
#     assert plugin is not None
#     assert inspect.isclass(plugin)
#
#
# def test_load_all_plugins():
#     plugin_names = ConfigXML.get_installed_plugins()
#     assert plugin_names
#
#     for cur_plugin_name in plugin_names:
#         cur_plugin = ConfigXML.find_plugin(cur_plugin_name)
#         assert cur_plugin is not None
#         assert inspect.isclass(cur_plugin)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
