import pytest
from pyjen.jenkins import Jenkins


def test_get_no_plugins(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results is not None
    assert isinstance(results, list)
    assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
