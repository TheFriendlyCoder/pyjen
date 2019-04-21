import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.buildblocker import BuildBlockerProperty
from pyjen.plugins.shellbuilder import ShellBuilder
from ..utils import async_assert, clean_job


def test_add_build_blocker(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_add_build_blocker"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_job_name = "MyCoolJob"
        build_blocker = BuildBlockerProperty.create(expected_job_name)
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        assert isinstance(properties, list)
        assert len(properties) == 1
        assert isinstance(properties[0], BuildBlockerProperty)


def test_multiple_blocking_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_multiple_blocking_jobs"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        build_blocker = BuildBlockerProperty.create(["ShouldNotSeeMe"])
        build_blocker.blockers = expected_jobs
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        blockers = prop.blockers
        assert isinstance(blockers, list)
        assert len(blockers) == 2
        assert expected_jobs[0] in blockers
        assert expected_jobs[1] in blockers


def test_default_queue_scan(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_default_queue_scan"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        build_blocker = BuildBlockerProperty.create(expected_jobs)
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        assert prop.queue_scan == "DISABLED"


def test_custom_queue_scan(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_custom_queue_scan"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        expected_type = "ALL"
        build_blocker = BuildBlockerProperty.create(expected_jobs)
        build_blocker.queue_scan = expected_type
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        assert prop.queue_scan == expected_type


def test_invalid_queue_scan_type():
    expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
    build_blocker = BuildBlockerProperty.create(expected_jobs)
    with pytest.raises(ValueError):
        build_blocker.queue_scan = "FuBar"


def test_default_block_level(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_default_block_level"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        build_blocker = BuildBlockerProperty.create(expected_jobs)
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        assert prop.level == "GLOBAL"


def test_custom_block_level(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_custom_block_level"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        expected_type = "NODE"
        build_blocker = BuildBlockerProperty.create(expected_jobs)
        build_blocker.level = expected_type
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        assert prop.level == expected_type


def test_invalid_block_level():
    expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
    build_blocker = BuildBlockerProperty.create(expected_jobs)
    with pytest.raises(ValueError):
        build_blocker.level = "FuBar"


def test_default_queue_scan(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_default_queue_scan"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        expected_jobs = ["MyCoolJob1", "MyCoolJob2"]
        build_blocker = BuildBlockerProperty.create(expected_jobs)
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        prop = properties[0]
        assert prop.queue_scan == "DISABLED"


def test_disable_build_blocker(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_disable_build_blocker"
    jb = jk.create_job(job_name, "hudson.model.FreeStyleProject")
    with clean_job(jb):
        build_blocker = BuildBlockerProperty.create("MyJob")
        build_blocker.disable()
        jb.quiet_period = 0
        jb.add_property(build_blocker)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).properties)
        properties = jk.find_job(job_name).properties

        assert properties[0].is_enabled is False


def test_build_blocker_functionality(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name1 = "test_build_blocker_functionality1"
    jb1 = jk.create_job(job_name1, "hudson.model.FreeStyleProject")
    with clean_job(jb1):
        job_name2 = "test_build_blocker_functionality2"
        jb2 = jk.create_job(job_name2, "hudson.model.FreeStyleProject")
        with clean_job(jb2):
            expected_jobs = job_name2
            build_blocker = BuildBlockerProperty.create(expected_jobs)
            jb1.quiet_period = 0
            jb1.add_property(build_blocker)

            # Get a fresh copy of our job to ensure we have an up to date
            # copy of the config.xml for the job
            async_assert(lambda: jk.find_job(job_name1).properties)

            build_step = ShellBuilder.create("sleep 10")
            jb2.quiet_period = 0
            jb2.add_builder(build_step)
            async_assert(lambda: jb2.builders)
            queue2 = jb2.start_build()

            async_assert(lambda: not queue2.waiting)

            queue1 = jb1.start_build()
            assert job_name2 in queue1.reason

            queue2.build.abort()
            assert queue1.waiting is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
