import pytest
import timeit
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ElementTree
from .utils import async_assert, clean_job
from pyjen.jenkins import Jenkins
from pyjen.plugins.freestylejob import FreestyleJob
from pyjen.build import Build
from pyjen.plugins.buildtriggerpublisher import BuildTriggerPublisher
from pyjen.plugins.shellbuilder import ShellBuilder


def test_create_freestyle_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_freestyle_job", FreestyleJob)
    with clean_job(jb):
        assert jb is not None


def test_delete_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_name = "test_delete_job"
    jb = jk.create_job(expected_name, FreestyleJob)
    jb.delete()
    res = jk.find_job(expected_name)
    assert res is None


def test_start_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_start_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        jb.start_build()


@pytest.mark.usefixtures('test_job')
class TestJobReadOperations(object):
    def test_get_job_name(self):
        # NOTE: The test_job fixture injects a Jenkins job named
        # read_only_test_job into the test server that we can leverage for
        # this test
        expected_name = "TestJobReadOperationsJob"
        assert self.job.name == expected_name

    def test_comparison_operators(self):
        jb2 = self.jenkins.find_job(self.job.name)

        assert self.job == jb2
        assert self.job != 10
        assert not self.job == 10

        jb3 = self.jenkins.create_job("test_comparison_operators", FreestyleJob)
        with clean_job(jb3):
            assert self.job != jb3

    def test_find_job(self):
        jb2 = self.jenkins.find_job(self.job.name)

        assert jb2 is not None
        assert jb2.name == self.job.name
        assert isinstance(jb2, FreestyleJob)

    def test_is_disabled_defaults(self):
        assert not self.job.is_disabled

    def test_has_not_been_built(self):
        assert not self.job.has_been_built

    def test_get_config_xml(self):
        res = self.job.config_xml
        assert res is not None
        xml = ElementTree.fromstring(res)
        assert xml.tag == "project"

    def test_no_downstream_jobs(self):
        dependencies = self.job.downstream_jobs

        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

    def test_no_upstream_jobs(self):
        dependencies = self.job.upstream_jobs

        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

    def test_get_no_recent_builds(self):
        builds = self.job.recent_builds

        assert isinstance(builds, list)
        assert len(builds) == 0

    def test_get_last_good_build_none(self):
        bld = self.job.last_good_build

        assert bld is None

    def test_get_last_build_none(self):
        bld = self.job.last_build

        assert bld is None

    def test_get_last_failed_build_none(self):
        bld = self.job.last_failed_build

        assert bld is None

    def test_get_last_stable_build_none(self):
        bld = self.job.last_stable_build

        assert bld is None

    def test_get_last_unsuccessful_build_none(self):
        bld = self.job.last_unsuccessful_build

        assert bld is None

    def test_get_build_by_number_non_existent(self):
        bld = self.job.get_build_by_number(1024)

        assert bld is None

    def test_no_build_health(self):
        score = self.job.build_health
        assert score == 0

    def test_no_publishers(self):
        pubs = self.job.publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 0

    def test_no_builders(self):
        builders = self.job.builders

        assert isinstance(builders, list)
        assert len(builders) == 0

    def test_no_properties(self):
        props = self.job.properties

        assert isinstance(props, list)
        assert len(props) == 0

    def test_null_scm(self):
        result = self.job.scm
        assert result is not None
        assert result.get_jenkins_plugin_name() == "hudson.scm.NullSCM"


def test_get_all_builds(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_all_builds", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        jb.start_build()
        async_assert(lambda: jb.all_builds)
        builds = jb.all_builds

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == 1


def test_disable(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_disable", FreestyleJob)
    with clean_job(jb):
        jb.disable()
        assert jb.is_disabled


def test_enable(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_enable", FreestyleJob)
    with clean_job(jb):
        jb.disable()
        jb.enable()
        assert not jb.is_disabled


def test_multiple_downstream_jobs_recursive(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_multiple_downstream_jobs_recursive1", FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_downstream_jobs_recursive2"
        jb2 = jk.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_downstream_jobs_recursive3"
            jb3 = jk.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                publisher1 = BuildTriggerPublisher.create([expected_name1])
                jb.add_publisher(publisher1)

                publisher2 = BuildTriggerPublisher.create([expected_name2])
                jb2.add_publisher(publisher2)

                async_assert(lambda: len(jb.all_downstream_jobs) == 2)
                res = jb.all_downstream_jobs

                all_names = [expected_name1, expected_name2]
                assert isinstance(res, list)
                assert len(res) == 2
                assert res[0].name in all_names
                assert res[1].name in all_names
                assert isinstance(res[0], FreestyleJob)
                assert isinstance(res[1], FreestyleJob)


def test_multiple_upstream_jobs_recursive(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent_job_name = "test_multiple_upstream_jobs_recursive1"
    jb = jk.create_job(parent_job_name, FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_upstream_jobs_recursive2"
        jb2 = jk.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_upstream_jobs_recursive3"
            jb3 = jk.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                publisher1 = BuildTriggerPublisher.create([expected_name1])
                jb.add_publisher(publisher1)

                publisher2 = BuildTriggerPublisher.create([expected_name2])
                jb2.add_publisher(publisher2)

                async_assert(lambda: len(jb3.all_upstream_jobs) == 2)
                res = jb3.all_upstream_jobs

                all_names = [parent_job_name, expected_name1]
                assert isinstance(res, list)
                assert len(res) == 2
                assert res[0].name in all_names
                assert res[1].name in all_names
                assert isinstance(res[0], FreestyleJob)
                assert isinstance(res[1], FreestyleJob)


@pytest.mark.usefixtures('test_builds')
class TestJobBuilds:

    def test_get_one_recent_build(self):
        builds = self.job.recent_builds

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == 1

    def test_get_last_good_build(self):
        bld = self.job.last_good_build

        assert isinstance(bld, Build)
        assert bld.number == 1

    def test_get_last_build(self):
        bld = self.job.last_build

        assert isinstance(bld, Build)
        assert bld.number == 1

    def test_get_last_stable_build(self):
        bld = self.job.last_stable_build

        assert isinstance(bld, Build)
        assert bld.number == 1

    def test_build_health(self):
        assert self.job.build_health == 100

    def test_has_been_built(self):
        assert self.job.has_been_built

    def test_get_build_by_number(self):
        bld = self.job.get_build_by_number(1)

        assert bld is not None
        assert bld.number == 1

    def test_get_builds_in_time_range(self):
        bld = self.job.last_build

        start_time = bld.start_time - timedelta(days=1)
        end_time = bld.start_time + timedelta(days=1)
        builds = self.job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

    def test_get_builds_in_time_range_no_builds_too_new(self):
        bld = self.job.last_build

        start_time = bld.start_time - timedelta(days=2)
        end_time = bld.start_time - timedelta(days=1)
        builds = self.job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 0

    def test_get_builds_in_time_range_no_builds_too_old(self):
        bld = self.job.last_build

        start_time = bld.start_time + timedelta(days=1)
        end_time = bld.start_time + timedelta(days=2)
        builds = self.job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 0

    def test_get_builds_in_time_range_upper_bound(self):
        bld = self.job.last_build

        start_time = bld.start_time - timedelta(days=1)
        end_time = bld.start_time
        builds = self.job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

    def test_get_builds_in_time_range_lower_bound(self):
        bld = self.job.last_build

        start_time = bld.start_time
        end_time = bld.start_time + timedelta(days=1)
        builds = self.job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

    def test_get_builds_in_time_range_inverted_parameters(self):

        bld = self.job.last_build

        start_time = bld.start_time
        end_time = bld.start_time + timedelta(days=1)
        builds = self.job.get_builds_in_time_range(end_time, start_time)

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number


def test_get_last_failed_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_failed_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        failing_step = ShellBuilder.create("exit -1")
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        jb.start_build()
        async_assert(lambda: jb.last_build)
        bld = jb.last_failed_build

        assert bld is not None
        assert isinstance(bld, Build)
        assert bld.number == 1
        assert bld.result == "FAILURE"


def test_get_last_unsuccessful_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_last_unsuccessful_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        rcode = 12
        failing_step = ShellBuilder.create("exit " + str(rcode))
        failing_step.unstable_return_code = rcode
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        jb.start_build()
        async_assert(lambda: jb.last_unsuccessful_build)
        bld = jb.last_unsuccessful_build

        assert bld is not None
        assert isinstance(bld, Build)
        assert bld.number == 1
        assert bld.result == "UNSTABLE"


def test_is_unstable(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_is_unstable_job", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        rcode = 12
        failing_step = ShellBuilder.create("exit " + str(rcode))
        failing_step.unstable_return_code = rcode
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        jb.start_build()
        async_assert(lambda: jb.last_unsuccessful_build)

        assert jb.is_unstable


def test_get_builds_in_time_range_no_builds(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_get_builds_in_time_range_no_builds", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now() + timedelta(days=1)
        builds = jb.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 0


def test_quiet_period(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_quiet_period", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        # first set our quiet period
        expected_duration = 10
        jb.quiet_period = expected_duration

        expected_output = "Testing my quiet period"
        failing_step = ShellBuilder.create("echo " + expected_output)
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        assert jb.quiet_period == expected_duration

        # Launch a build and time how long it takes to complete
        start = timeit.default_timer()
        jb.start_build()
        async_assert(lambda: jb.last_build, expected_duration + 5)
        duration = timeit.default_timer() - start
        assert duration >= expected_duration

        bld = jb.last_build
        assert expected_output in bld.console_output


def test_clone_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job", FreestyleJob)
    with clean_job(jb):
        # add a builder to our source job so we can check to make sure the
        # configuration has been properly cloned
        expected_script = "echo Hello From TestCloneJob"
        failing_step = ShellBuilder.create(expected_script)
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        # now, clone our job configuration and make sure the entire config
        # has been cloned correctly
        expected_name = "test_clone_job2"
        jb_clone = jb.clone(expected_name)
        with clean_job(jb_clone):
            assert jb_clone is not None
            assert jb_clone.name == expected_name
            assert jb_clone.is_disabled
            results = jb_clone.builders
            assert results is not None
            assert isinstance(results, list)
            assert len(results) == 1
            assert isinstance(results[0], ShellBuilder)
            assert results[0].script == expected_script


def test_clone_job_enabled(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job_enabled", FreestyleJob)
    with clean_job(jb):
        jb_clone = jb.clone("test_clone_job2", False)
        with clean_job(jb_clone):
            assert jb_clone is not None
            assert jb_clone.is_disabled is False


def test_rename_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    original_job_name = "test_rename_job1"
    new_job_name = "test_rename_job2"
    jb = jk.create_job(original_job_name, FreestyleJob)
    try:
        jb.rename(new_job_name)
        assert jk.find_job(original_job_name) is None
        jb_copy = jk.find_job(new_job_name)
        assert jb_copy is not None
        assert jb.name == new_job_name
        assert jb_copy == jb
    finally:
        tmp = jk.find_job(original_job_name)
        if tmp:
            tmp.delete()

        tmp = jk.find_job(new_job_name)
        if tmp:
            tmp.delete()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
