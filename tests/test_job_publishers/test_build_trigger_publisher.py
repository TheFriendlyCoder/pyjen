import time
import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.buildtriggerpublisher import BuildTriggerPublisher


def test_add_build_trigger_publisher(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    upstream_name = "test_add_build_trigger_publisher1"
    jb = jk.create_job(upstream_name, "project")
    jb2 = None
    try:
        downstream_name = "test_add_build_trigger_publisher2"
        jb2 = jk.create_job(downstream_name, "project")
        publisher = BuildTriggerPublisher.create(downstream_name)
        jb.add_publisher(publisher)
        # TODO: Find more robust way to detect when asynchronous calls are finished
        #       Idea: look at Jenkins server logs to see if there is status info
        #       we can use to figure this out
        time.sleep(5)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        tmp = jk.find_job(upstream_name)
        pubs = tmp.publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 1
        assert isinstance(pubs[0], BuildTriggerPublisher)
        names = pubs[0].job_names
        assert isinstance(names, list)
        assert len(names) == 1
        assert names[0] == downstream_name
    finally:
        jb.delete()
        if jb2:
            jb2.delete()


def test_downstream_jobs(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_downstream_jobs1", "project")
    jb2 = None
    try:
        expected_name = "test_downstream_jobs2"
        jb2 = jk.create_job(expected_name, "project")
        publisher = BuildTriggerPublisher.create(expected_name)
        jb.add_publisher(publisher)
        time.sleep(5)
        res = jb.downstream_jobs

        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0].name == expected_name
    finally:
        jb.delete()
        if jb2:
            jb2.delete()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
