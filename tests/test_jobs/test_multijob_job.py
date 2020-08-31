from ..utils import clean_job
from pyjen.plugins.multijob import MultiJob


def test_create_multijob_job(jenkins_api):
    expected_name = "test_create_multijob_job"
    jb = jenkins_api.create_job(expected_name, MultiJob)
    with clean_job(jb):
        assert jb is not None
        assert jb.name == expected_name
