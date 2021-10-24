import pytest
from ..utils import clean_job, async_assert
from pyjen.plugins.gitscm import GitSCM
from pyjen.plugins.pipelinejob import PipelineJob


def test_create_pipeline_job(jenkins_api):
    jb = jenkins_api.create_job("test_create_pipeline_job", PipelineJob)
    with clean_job(jb):
        assert jb is not None


@pytest.mark.skip(reason="To be fixed")
def test_groovy_script_pipeline_job(jenkins_api):
    jb = jenkins_api.create_job("test_groovy_script_pipeline_job", PipelineJob)
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


def test_git_scm_pipeline_job(jenkins_api):
    jb = jenkins_api.create_job("test_git_scm_pipeline_job", PipelineJob)
    with clean_job(jb):
        expected_url = "git@repo.com"
        scm = GitSCM.instantiate(expected_url)
        jb.scm_definition(scm)

        assert jb.script == ""
        result = jb.scm
        assert result is not None
        assert isinstance(result, GitSCM)
        assert result.url == expected_url
        assert jb.script == ""


@pytest.mark.skip(reason="To be fixed")
def test_overwrite_definition(jenkins_api):
    jb = jenkins_api.create_job("test_overwrite_definition", PipelineJob)
    with clean_job(jb):
        expected_url = "git@repo.com"
        scm = GitSCM.instantiate(expected_url)
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
