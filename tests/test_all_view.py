from pyjen.jenkins import Jenkins
from pyjen.plugins.allview import AllView
import pytest


def test_find_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "all"
    v = jk.find_view(expected_name).derived_object

    assert isinstance(v, AllView)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
