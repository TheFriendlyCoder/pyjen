import pytest
from ..utils import clean_job
from pyjen.jenkins import Jenkins
from pyjen.plugins.multijob import MultiJob


def test_create_multijob_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_create_multijob_job"
    jb = jk.create_job(expected_name, MultiJob)
    with clean_job(jb):
        assert jb is not None
        assert jb.name == expected_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
