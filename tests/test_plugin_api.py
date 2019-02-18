import pytest
import inspect
from pyjen.utils.configxml import ConfigXML
from .utils import count_plugins


def test_list_plugins():
    res = ConfigXML.get_installed_plugins()
    assert res is not None
    assert isinstance(res, list)
    assert len(res) == count_plugins()


def test_find_plugins():
    plugin_names = ConfigXML.get_installed_plugins()
    assert plugin_names

    plugin = ConfigXML.find_plugin(plugin_names[0])
    assert plugin is not None
    assert inspect.isclass(plugin)


def test_load_all_plugins():
    plugin_names = ConfigXML.get_installed_plugins()
    assert plugin_names

    for cur_plugin_name in plugin_names:
        cur_plugin = ConfigXML.find_plugin(cur_plugin_name)
        assert cur_plugin is not None
        assert inspect.isclass(cur_plugin)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
