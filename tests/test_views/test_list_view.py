from pyjen.jenkins import Jenkins
import pytest
from pyjen.plugins.listview import ListView
from ..utils import clean_view


def test_create_list_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_create_list_view"
    v = jk.create_view(expected_view_name, "hudson.model.ListView")
    assert v is not None
    with clean_view(v):
        assert v.name == expected_view_name


def test_list_view_derived(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_list_view_derived"
    v = jk.create_view(expected_view_name, "hudson.model.ListView")
    assert v is not None
    with clean_view(v):
        assert isinstance(v.derived_object, ListView)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
