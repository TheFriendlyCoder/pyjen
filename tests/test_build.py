from datetime import datetime
import pytest
from .utils import clean_job, async_assert
from pyjen.plugins.shellbuilder import ShellBuilder
from pyjen.plugins.freestylejob import FreestyleJob


@pytest.mark.vcr()
def test_single_build(jenkins_api):
    job = jenkins_api.create_job("test_single_build_job", FreestyleJob)
    with clean_job(job):
        job.quiet_period = 0
        job.start_build()

        async_assert(lambda: job.last_good_build)
        last_build = job.last_build
        assert last_build.number == 1
        assert last_build.is_building is False
        assert last_build.description == ''

        expected_description = 'Test description'
        last_build.description = expected_description
        assert last_build.description == expected_description

        last_good_build = job.last_good_build
        assert last_good_build.result == "SUCCESS"
        assert last_build.uid == '1'

        bld1 = job.all_builds[0]

        assert bld1 == last_good_build
        assert not bld1 != last_good_build


@pytest.mark.skip(reason="To be fixed")
def test_start_time(jenkins_api):
    jb = jenkins_api.create_job("test_start_time_job", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        before = datetime.now()
        jb.start_build()
        async_assert(lambda: jb.last_build)
        after = datetime.now()

        bld = jb.last_build
        assert before <= bld.start_time <= after


@pytest.mark.vcr()
def test_build_inequality(jenkins_api):
    jb = jenkins_api.create_job("test_build_inequality_job", FreestyleJob)
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


@pytest.mark.vcr()
def test_console_text(jenkins_api):
    expected_job_name = "test_console_text_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.instantiate("echo " + expected_output)
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(expected_job_name).builders)

        # Trigger a build and wait for it to complete
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output in jb.last_build.console_output


@pytest.mark.vcr()
@pytest.mark.timeout(10)
def test_abort(jenkins_api):
    expected_job_name = "test_abort"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)

    with clean_job(jb):
        jb.quiet_period = 0
        shell_builder = ShellBuilder.instantiate("echo 'waiting for sleep' && sleep 40")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(expected_job_name).builders)

        # Trigger a build and wait for it to complete
        jb.start_build()
        async_assert(lambda: jb.last_build)

        async_assert(lambda: "waiting for sleep" in jb.last_build.console_output)

        jb.last_build.abort()

        assert jb.last_build.is_building is False
        assert jb.last_build.result == "ABORTED"
