import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.artifactdeployer import ArtifactDeployer, ArtifactDeployerEntry
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


def test_add_artifact_deployer_publisher(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_add_artifact_deployer_publisher"
    jb = jk.create_job(job_name, FreestyleJob)
    with clean_job(jb):
        publisher = ArtifactDeployer.create()
        jb.add_publisher(publisher)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).publishers)
        pubs = jk.find_job(job_name).publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 1
        assert isinstance(pubs[0], ArtifactDeployer)
        assert isinstance(pubs[0].entries, list)
        assert len(pubs[0].entries) == 0


def test_add_artifact_deployer_publisher_entry(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_add_artifact_deployer_publisher_entry"
    jb = jk.create_job(job_name, FreestyleJob)
    with clean_job(jb):
        publisher = ArtifactDeployer.create()
        jb.add_publisher(publisher)

        expected_regex = "*.txt"
        expected_path = "/bin/data"
        entry = ArtifactDeployerEntry.create(expected_regex, expected_path)
        publisher.add_entry(entry)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).publishers)
        pubs = jk.find_job(job_name).publishers

        assert len(pubs) == 1
        cur_pub = pubs[0]
        assert isinstance(cur_pub, ArtifactDeployer)
        assert isinstance(cur_pub.entries, list)
        assert len(cur_pub.entries) == 1
        cur_entry = cur_pub.entries[0]
        assert isinstance(cur_entry, ArtifactDeployerEntry)
        assert cur_entry.includes == expected_regex
        assert cur_entry.remote == expected_path


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
