from pyjen.jenkins import Jenkins
import pytest
from .utils import clean_view, clean_job


def test_delete_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_delete_view"
    vw = jk.create_view(expected_view_name, "hudson.model.ListView")
    vw.delete()
    assert jk.find_view(expected_view_name) is None


def test_get_name(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_get_name_view"
    vw = jk.create_view(expected_name, "hudson.model.ListView")
    with clean_view(vw):
        assert vw.name == expected_name


def test_get_jobs_no_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    vw = jk.create_view("test_get_jobs_no_jobs_views", "hudson.model.ListView")
    with clean_view(vw):
        jobs = vw.jobs
        assert isinstance(jobs, list)
        assert len(jobs) == 0


def test_get_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_get_jobs_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        vw = jk.default_view
        all_jobs = vw.jobs
        assert isinstance(all_jobs, list)
        assert len(all_jobs) == 1
        assert all_jobs[0].name == expected_job_name


def test_delete_all_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_delete_all_jobs_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")

    try:
        vw = jk.default_view
        assert len(vw.jobs) == 1
        vw.delete_all_jobs()
        assert len(vw.jobs) == 0
    except:
        # In case our delete operation doesn't complete successfully, we do
        # a manual deletion here to keep our test environment clean
        jb.delete()
        raise


def test_disable_all_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_disable_all_jobs_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")

    with clean_job(jb):
        vw = jk.default_view
        vw.disable_all_jobs()
        assert jb.is_disabled


def test_enable_all_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_enable_all_jobs_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")

    with clean_job(jb):
        vw = jk.default_view
        jb.disable()
        vw.enable_all_jobs()
        assert jb.is_disabled is False


def test_get_config_xml(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))

    assert jk.default_view.config_xml


def test_get_view_metrics(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_get_view_metrics_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        jb.disable()
        result = jk.default_view.view_metrics
        expected_keys = [
            'unstable_jobs',
            'unstable_jobs_count',
            'broken_jobs_count',
            'disabled_jobs',
            'disabled_jobs_count',
            'broken_jobs'
        ]

        for cur_key in expected_keys:
            assert cur_key in result.keys()
        assert result['broken_jobs_count'] == 0
        assert result['disabled_jobs_count'] == 1
        assert result['unstable_jobs_count'] == 0
        assert isinstance(result['disabled_jobs'], list)
        assert len(result['disabled_jobs']) == 1
        assert result['disabled_jobs'][0].name == expected_job_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
