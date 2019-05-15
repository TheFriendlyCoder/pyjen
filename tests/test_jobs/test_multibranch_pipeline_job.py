import pytest
from ..utils import clean_job
from pyjen.jenkins import Jenkins
from pyjen.plugins.multibranch_pipeline import MultibranchPipelineJob


def test_create_multibranch_pipeline_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_create_multibranch_pipeline_job"
    jb = jk.create_job(expected_name, MultibranchPipelineJob)
    with clean_job(jb):
        assert jb is not None
        assert jb.name == expected_name


def test_get_branch_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_get_branch_jobs"
    jb = jk.create_job(expected_name, MultibranchPipelineJob)
    with clean_job(jb):
        res = jb.jobs

        assert res is not None
        assert isinstance(res, list)
        assert len(res) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
