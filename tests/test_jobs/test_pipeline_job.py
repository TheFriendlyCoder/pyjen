import pytest
from ..utils import clean_job, async_assert
from pyjen.jenkins import Jenkins
from pyjen.plugins.gitscm import GitSCM
from pyjen.plugins.pipelinejob import PipelineJob


def test_create_pipeline_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_pipeline_job", PipelineJob)
    with clean_job(jb):
        assert jb is not None


def test_groovy_script_pipeline_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_groovy_script_pipeline_job", PipelineJob)
    with clean_job(jb):
        jb.quiet_period = 0
        expected_output = "hello"
        expected_cmd = 'echo "{}"'.format(expected_output)
        jb.script_definition(expected_cmd)
        jb.start_build()

        async_assert(lambda: jb.last_good_build)
        assert jb.script == expected_cmd
        assert jb.scm is None
        assert expected_output in jb.last_build.console_output


def test_git_scm_pipeline_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_git_scm_pipeline_job", PipelineJob)
    with clean_job(jb):
        expected_url = "git@repo.com"
        scm = GitSCM.create(expected_url)
        jb.scm_definition(scm)

        assert jb.script == ""
        result = jb.scm
        assert result is not None
        assert isinstance(result, GitSCM)
        assert result.url == expected_url
        assert jb.script == ""


def test_overwrite_definition(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_overwrite_definition", PipelineJob)
    with clean_job(jb):
        expected_url = "git@repo.com"
        scm = GitSCM.create(expected_url)
        jb.scm_definition(scm)

        jb.quiet_period = 0
        expected_output = "hello"
        expected_cmd = 'echo "{}"'.format(expected_output)
        jb.script_definition(expected_cmd)
        jb.start_build()

        async_assert(lambda: jb.last_good_build)
        assert jb.script == expected_cmd
        assert jb.scm is None
        assert expected_output in jb.last_build.console_output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
