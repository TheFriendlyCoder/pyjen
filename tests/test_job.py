import pytest
import timeit
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ElementTree
from .utils import async_assert, clean_job
from pyjen.plugins.freestylejob import FreestyleJob
from pyjen.build import Build
from pyjen.plugins.buildtriggerpublisher import BuildTriggerPublisher
from pyjen.plugins.shellbuilder import ShellBuilder
from pyjen.plugins.nullscm import NullSCM


@pytest.mark.vcr()
def test_create_freestyle_job(jenkins_api):
    jb = jenkins_api.create_job("test_create_freestyle_job", FreestyleJob)
    with clean_job(jb):
        assert jb is not None


@pytest.mark.vcr()
def test_delete_job(jenkins_api):
    expected_name = "test_delete_job"
    jb = jenkins_api.create_job(expected_name, FreestyleJob)
    jb.delete()
    res = jenkins_api.find_job(expected_name)
    assert res is None


@pytest.mark.vcr()
def test_start_build(jenkins_api):
    jb = jenkins_api.create_job("test_start_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        jb.start_build()


@pytest.mark.vcr()
def test_job_read_operations(jenkins_api):
    expected_name = "test_job_read_operations"
    job = jenkins_api.create_job(expected_name, FreestyleJob)
    with clean_job(job):
        assert job.name == expected_name

        jb2 = jenkins_api.find_job(expected_name)
        assert jb2 is not None
        assert isinstance(jb2, FreestyleJob)
        assert jb2.name == job.name

        assert job == jb2
        assert job != 10
        assert not job == 10
        jb3 = jenkins_api.create_job("test_comparison_operators", FreestyleJob)
        with clean_job(jb3):
            assert job != jb3

        assert not job.is_disabled
        assert not job.has_been_built
        res = job.config_xml
        assert res is not None
        xml = ElementTree.fromstring(res)
        assert xml.tag == "project"

        dependencies = job.downstream_jobs
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

        dependencies = job.upstream_jobs
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0

        builds = job.recent_builds
        assert isinstance(builds, list)
        assert len(builds) == 0

        bld = job.last_good_build
        assert bld is None

        bld = job.last_build
        assert bld is None

        bld = job.last_failed_build
        assert bld is None

        bld = job.last_stable_build
        assert bld is None

        bld = job.last_unsuccessful_build
        assert bld is None

        bld = job.get_build_by_number(1024)
        assert bld is None

        score = job.build_health
        assert score == 0

        pubs = job.publishers
        assert isinstance(pubs, list)
        assert len(pubs) == 0

        builders = job.builders
        assert isinstance(builders, list)
        assert len(builders) == 0

        props = job.properties
        assert isinstance(props, list)
        assert len(props) == 0

        result = job.scm
        assert result is not None
        assert isinstance(result, NullSCM)


@pytest.mark.vcr()
def test_get_all_builds(jenkins_api):
    jb = jenkins_api.create_job("test_get_all_builds", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        jb.start_build()
        async_assert(lambda: jb.all_builds)
        builds = jb.all_builds

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == 1


@pytest.mark.vcr()
def test_disable(jenkins_api):
    jb = jenkins_api.create_job("test_disable", FreestyleJob)
    with clean_job(jb):
        jb.disable()
        assert jb.is_disabled


@pytest.mark.vcr()
def test_enable(jenkins_api):
    jb = jenkins_api.create_job("test_enable", FreestyleJob)
    with clean_job(jb):
        jb.disable()
        jb.enable()
        assert not jb.is_disabled


@pytest.mark.vcr()
def test_multiple_downstream_jobs_recursive(jenkins_api):
    jb = jenkins_api.create_job("test_multiple_downstream_jobs_recursive1", FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_downstream_jobs_recursive2"
        jb2 = jenkins_api.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_downstream_jobs_recursive3"
            jb3 = jenkins_api.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                publisher1 = BuildTriggerPublisher.instantiate([expected_name1])
                jb.add_publisher(publisher1)

                publisher2 = BuildTriggerPublisher.instantiate([expected_name2])
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


@pytest.mark.vcr()
def test_multiple_upstream_jobs_recursive(jenkins_api):
    parent_job_name = "test_multiple_upstream_jobs_recursive1"
    jb = jenkins_api.create_job(parent_job_name, FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_upstream_jobs_recursive2"
        jb2 = jenkins_api.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_upstream_jobs_recursive3"
            jb3 = jenkins_api.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                publisher1 = BuildTriggerPublisher.instantiate([expected_name1])
                jb.add_publisher(publisher1)

                publisher2 = BuildTriggerPublisher.instantiate([expected_name2])
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


@pytest.mark.vcr()
def test_job_builds(jenkins_api):
    job = jenkins_api.create_job("test_job_builds", FreestyleJob)
    with clean_job(job):
        job.quiet_period = 0
        job.start_build()

        async_assert(lambda: job.last_good_build)

        builds = job.recent_builds

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == 1

        bld = job.last_good_build
        assert isinstance(bld, Build)
        assert bld.number == 1

        bld = job.last_build
        assert isinstance(bld, Build)
        assert bld.number == 1

        bld = job.last_stable_build
        assert isinstance(bld, Build)
        assert bld.number == 1

        assert job.build_health == 100
        assert job.has_been_built

        bld = job.get_build_by_number(1)
        assert bld is not None
        assert bld.number == 1

        bld = job.last_build
        start_time = bld.start_time - timedelta(days=1)
        end_time = bld.start_time + timedelta(days=1)
        builds = job.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

        bld = job.last_build
        start_time = bld.start_time - timedelta(days=2)
        end_time = bld.start_time - timedelta(days=1)
        builds = job.get_builds_in_time_range(start_time, end_time)
        assert len(builds) == 0

        bld = job.last_build
        start_time = bld.start_time + timedelta(days=1)
        end_time = bld.start_time + timedelta(days=2)
        builds = job.get_builds_in_time_range(start_time, end_time)
        assert len(builds) == 0

        bld = job.last_build
        start_time = bld.start_time - timedelta(days=1)
        end_time = bld.start_time
        builds = job.get_builds_in_time_range(start_time, end_time)
        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

        bld = job.last_build
        start_time = bld.start_time
        end_time = bld.start_time + timedelta(days=1)
        builds = job.get_builds_in_time_range(start_time, end_time)
        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number

        bld = job.last_build
        start_time = bld.start_time
        end_time = bld.start_time + timedelta(days=1)
        builds = job.get_builds_in_time_range(end_time, start_time)
        assert len(builds) == 1
        assert isinstance(builds[0], Build)
        assert builds[0].number == bld.number


@pytest.mark.vcr()
def test_get_last_failed_build(jenkins_api):
    jb = jenkins_api.create_job("test_get_last_failed_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        failing_step = ShellBuilder.instantiate("exit -1")
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        jb.start_build()
        async_assert(lambda: jb.last_build)
        bld = jb.last_failed_build

        assert bld is not None
        assert isinstance(bld, Build)
        assert bld.number == 1
        assert bld.result == "FAILURE"


@pytest.mark.vcr()
def test_get_last_unsuccessful_build(jenkins_api):
    jb = jenkins_api.create_job("test_get_last_unsuccessful_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        rcode = 12
        failing_step = ShellBuilder.instantiate("exit " + str(rcode))
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


@pytest.mark.vcr()
def test_is_unstable(jenkins_api):
    jb = jenkins_api.create_job("test_is_unstable_job", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        rcode = 12
        failing_step = ShellBuilder.instantiate("exit " + str(rcode))
        failing_step.unstable_return_code = rcode
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        jb.start_build()
        async_assert(lambda: jb.last_unsuccessful_build)

        assert jb.is_unstable


@pytest.mark.vcr()
def test_get_builds_in_time_range_no_builds(jenkins_api):
    jb = jenkins_api.create_job("test_get_builds_in_time_range_no_builds", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now() + timedelta(days=1)
        builds = jb.get_builds_in_time_range(start_time, end_time)

        assert len(builds) == 0


@pytest.mark.vcr()
def test_no_quiet_period(jenkins_api):
    jb = jenkins_api.create_job("test_no_quiet_period", FreestyleJob)
    with clean_job(jb):
        assert jb.quiet_period_enabled is False
        assert jb.quiet_period == -1


@pytest.mark.vcr()
def test_quiet_period(jenkins_api):
    jb = jenkins_api.create_job("test_quiet_period", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        # first set our quiet period
        expected_duration = 10
        jb.quiet_period = expected_duration

        expected_output = "Testing my quiet period"
        failing_step = ShellBuilder.instantiate("echo " + expected_output)
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        assert jb.quiet_period_enabled is True
        assert jb.quiet_period == expected_duration

        # Launch a build and time how long it takes to complete
        start = timeit.default_timer()
        jb.start_build()
        async_assert(lambda: jb.last_build, expected_duration + 5)
        duration = timeit.default_timer() - start
        assert float(expected_duration) == pytest.approx(duration, 0.8)

        bld = jb.last_build
        assert expected_output in bld.console_output


@pytest.mark.vcr()
def test_disable_quiet_period(jenkins_api):
    jb = jenkins_api.create_job("test_disable_quiet_period", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0

        jb2 = jenkins_api.find_job(jb.name)
        assert jb2 is not None
        jb2.quiet_period = -1
        assert jb2.quiet_period_enabled is False


@pytest.mark.vcr()
def test_no_custom_workspace(jenkins_api):
    jb = jenkins_api.create_job("test_no_custom_workspace", FreestyleJob)
    with clean_job(jb):
        assert jb.custom_workspace_enabled is False
        assert jb.custom_workspace == ""


@pytest.mark.vcr()
def test_custom_workspace(jenkins_api):
    jb = jenkins_api.create_job("test_custom_workspace", FreestyleJob)
    with clean_job(jb):
        expected_workspace = "/delme"
        jb.custom_workspace = expected_workspace

        jb2 = jenkins_api.find_job(jb.name)
        assert jb2.custom_workspace_enabled is True
        assert jb2.custom_workspace == expected_workspace


@pytest.mark.vcr()
def test_disable_custom_workspace(jenkins_api):
    jb = jenkins_api.create_job("test_disable_custom_workspace", FreestyleJob)
    with clean_job(jb):
        jb.custom_workspace = "/delme"

        jb2 = jenkins_api.find_job(jb.name)
        jb2.custom_workspace = ""
        assert jb2.custom_workspace_enabled is False


@pytest.mark.vcr()
def test_no_assigned_node(jenkins_api):
    jb = jenkins_api.create_job("test_no_assigned_node", FreestyleJob)
    with clean_job(jb):
        assert jb.assigned_node_enabled is False
        assert jb.assigned_node == ""


@pytest.mark.vcr()
def test_assigned_node(jenkins_api):
    jb = jenkins_api.create_job("test_assigned_node", FreestyleJob)
    with clean_job(jb):
        expected_label = "MyNodeLabel && UnknownLabel"
        jb.assigned_node = expected_label

        jb2 = jenkins_api.find_job(jb.name)
        assert jb2.assigned_node_enabled is True
        assert jb2.assigned_node == expected_label


@pytest.mark.vcr()
def test_disable_assigned_node(jenkins_api):
    jb = jenkins_api.create_job("test_disable_assigned_node", FreestyleJob)
    with clean_job(jb):
        jb.assigned_node = "MyNodeLabel && UnknownLabel"

        jb2 = jenkins_api.find_job(jb.name)
        jb2.assigned_node = ""
        assert jb2.assigned_node_enabled is False


@pytest.mark.vcr()
def test_clone_job(jenkins_api):
    jb = jenkins_api.create_job("test_clone_job", FreestyleJob)
    with clean_job(jb):
        # add a builder to our source job so we can check to make sure the
        # configuration has been properly cloned
        expected_script = "echo Hello From TestCloneJob"
        failing_step = ShellBuilder.instantiate(expected_script)
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


@pytest.mark.vcr()
def test_clone_job_enabled(jenkins_api):
    jb = jenkins_api.create_job("test_clone_job_enabled", FreestyleJob)
    with clean_job(jb):
        jb_clone = jb.clone("test_clone_job2", False)
        with clean_job(jb_clone):
            assert jb_clone is not None
            assert jb_clone.is_disabled is False


@pytest.mark.vcr()
def test_rename_job(jenkins_api):
    original_job_name = "test_rename_job1"
    new_job_name = "test_rename_job2"
    jb = jenkins_api.create_job(original_job_name, FreestyleJob)
    try:
        jb.rename(new_job_name)
        assert jenkins_api.find_job(original_job_name) is None
        jb_copy = jenkins_api.find_job(new_job_name)
        assert jb_copy is not None
        assert jb.name == new_job_name
        assert jb_copy == jb
    finally:
        tmp = jenkins_api.find_job(original_job_name)
        if tmp:
            tmp.delete()

        tmp = jenkins_api.find_job(new_job_name)
        if tmp:
            tmp.delete()


@pytest.mark.vcr()
def test_find_build_by_queue_id_match(jenkins_api):
    jb = jenkins_api.create_job("test_find_build_by_queue_id_match", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        q1 = jb.start_build()
        async_assert(lambda: jb.last_build)
        bld1 = q1.build
        assert bld1 is not None

        bld2 = jb.find_build_by_queue_id(q1.uid)
        assert bld1 == bld2


@pytest.mark.vcr()
def test_find_build_by_queue_id_no_match(jenkins_api):
    jb = jenkins_api.create_job("test_find_build_by_queue_id_no_match", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        q1 = jb.start_build()
        test_id = q1.uid + 50
        async_assert(lambda: jb.last_build)

        bld = jb.find_build_by_queue_id(test_id)
        assert bld is None
