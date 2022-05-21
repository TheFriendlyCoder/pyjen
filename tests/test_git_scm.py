import pytest
from pyjen.plugins.gitscm import GitSCM
from pyjen.plugins.shellbuilder import ShellBuilder
from pyjen.plugins.freestylejob import FreestyleJob
from .utils import clean_job, async_assert


def test_add_git_scm(jenkins_api):
    job_name = "test_add_git_scm"
    jb = jenkins_api.create_job(job_name, FreestyleJob)
    with clean_job(jb):
        expected_url = "https://github.com/TheFriendlyCoder/pyjen.git"
        test_scm = GitSCM.instantiate(expected_url)
        jb.scm = test_scm

        async_assert(lambda: isinstance(jb.scm, GitSCM))

        jb2 = jenkins_api.find_job(job_name)

        result = jb2.scm
        assert result is not None
        assert isinstance(result, GitSCM)


@pytest.mark.skip(reason="To be fixed")
def test_build_git_scm(jenkins_api):
    job_name = "test_build_git_scm"
    jb = jenkins_api.create_job(job_name, FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        expected_url = "https://github.com/TheFriendlyCoder/pyjen.git"
        test_scm = GitSCM.instantiate(expected_url)
        jb.scm = test_scm

        async_assert(lambda: isinstance(jb.scm, GitSCM))

        # If the Git SCM was set up correctly, the job should check out the
        # source code for pyjen into the workspace when building. That being
        # the case there should be a setup.py script in the root folder. We
        # can therefore check to see if the SCM operation completed successfully
        # by looking for that file and setting a non-zero error code as part
        # of a shell builder operation
        shell_builder = ShellBuilder.instantiate("[ -f setup.py ]")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(job_name).builders)

        jb.start_build()
        async_assert(lambda: jb.last_good_build or jb.last_failed_build)

        assert jb.last_good_build is not None
