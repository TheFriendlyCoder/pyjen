from datetime import datetime
import pytest
from .utils import clean_job, async_assert
from pyjen.jenkins import Jenkins
from pyjen.plugins.shellbuilder import ShellBuilder


@pytest.mark.usefixtures('test_builds')
class TestSingleBuild:
    def test_build_number(self):
        bld = self.job.last_build
        assert bld.number == 1

    def test_is_not_building(self):
        bld = self.job.last_build
        assert bld.is_building is False

    def test_build_no_description(self):
        bld = self.job.last_build
        assert bld.description == ''

    def test_build_result(self):
        bld = self.job.last_good_build
        assert bld.result == "SUCCESS"

    def test_build_id(self):
        bld = self.job.last_build
        assert bld.id == '1'

    def test_build_equality(self):
        bld1 = self.job.all_builds[0]
        bld2 = self.job.last_build

        assert bld1 == bld2
        assert not bld1 != bld2


def test_start_time(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_start_time_job", "hudson.model.FreeStyleProject")
    with clean_job(jb):
        jb.quiet_period = 0
        before = datetime.now()
        jb.start_build()
        async_assert(lambda: jb.last_build)
        after = datetime.now()

        bld = jb.last_build
        assert before <= bld.start_time <= after


def test_build_inequality(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_build_inequality_job", "hudson.model.FreeStyleProject")
    with clean_job(jb):
        jb.quiet_period = 0
        jb.start_build()
        async_assert(lambda: len(jb.all_builds) == 1)
        jb.start_build()
        async_assert(lambda: len(jb.all_builds) == 2)

        bld1 = jb.all_builds[0]
        bld2 = jb.all_builds[1]

        assert bld1 != bld2
        assert not bld1 == bld2
        assert bld1 != 1


def test_console_text(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_console_text_job"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        jb.quiet_period = 0
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.create("echo " + expected_output)
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        # Trigger a build and wait for it to complete
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output in jb.last_build.console_output


@pytest.mark.timeout(10)
def test_abort(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_abort"
    jb = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")

    with clean_job(jb):
        jb.quiet_period = 0
        shell_builder = ShellBuilder.create("echo 'waiting for sleep' && sleep 40")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        # Trigger a build and wait for it to complete
        jb.start_build()
        async_assert(lambda: jb.last_build)

        async_assert(lambda: "waiting for sleep" in jb.last_build.console_output)

        jb.last_build.abort()

        assert jb.last_build.is_building is False
        assert jb.last_build.result == "ABORTED"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
