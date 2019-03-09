from pyjen.jenkins import Jenkins
from pyjen.plugins.allview import AllView
import pytest
from mock import patch, MagicMock


def test_find_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "all"
    v = jk.find_view(expected_name).derived_object

    assert isinstance(v, AllView)


def test_derived_no_plugin(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "all"
    v = jk.find_view(expected_name)

    with patch("pyjen.utils.plugin_api.iter_entry_points") as entry_points:
        mock_plugin_class = MagicMock(spec=[])
        mock_ep = MagicMock()
        mock_ep.load.return_value = mock_plugin_class
        entry_points.return_value = [mock_ep]

        # Calling derived_object on an object with no plugin should just return
        # the original object reference as a fallback
        assert v.derived_object is v


def test_derived_object_twice(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "all"
    v = jk.find_view(expected_name).derived_object

    # Calling derived_object on a derived object should just return itself
    assert v.derived_object is v


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
