from ..utils import clean_job
from pyjen.plugins.multibranch_pipeline import MultibranchPipelineJob


def test_create_multibranch_pipeline_job(jenkins_api):
    expected_name = "test_create_multibranch_pipeline_job"
    jb = jenkins_api.create_job(expected_name, MultibranchPipelineJob)
    with clean_job(jb):
        assert jb is not None
        assert jb.name == expected_name


def test_get_branch_jobs(jenkins_api):
    expected_name = "test_get_branch_jobs"
    jb = jenkins_api.create_job(expected_name, MultibranchPipelineJob)
    with clean_job(jb):
        res = jb.jobs

        assert res is not None
        assert isinstance(res, list)
        assert len(res) == 0
