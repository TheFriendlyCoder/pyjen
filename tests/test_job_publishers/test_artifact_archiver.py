import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.artifactarchiver import ArtifactArchiverPublisher
from pyjen.plugins.shellbuilder import ShellBuilder
from ..utils import async_assert, clean_job


def test_add_artifact_archiver_publisher(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_add_artifact_archiver_publisher_job"
    jb = jk.create_job(job_name, "project")
    with clean_job(jb):
        expected_regex = "*.txt"
        publisher = ArtifactArchiverPublisher.create(expected_regex)
        jb.add_publisher(publisher)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).publishers)
        pubs = jk.find_job(job_name).publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 1
        assert isinstance(pubs[0], ArtifactArchiverPublisher)
        assert pubs[0].artifact_regex == expected_regex


def test_artifacts_archived(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_artifacts_archived_job"
    jb = jk.create_job(job_name, "project")
    with clean_job(jb):
        publisher = ArtifactArchiverPublisher.create("*.txt")
        jb.add_publisher(publisher)

        # Wait until our publisher config get's applied
        async_assert(lambda: jk.find_job(job_name).publishers)

        expected_file = "test_artifacts_archived_job.txt"
        shell_builder = ShellBuilder.create("echo hello > " + expected_file)
        jb.add_builder(shell_builder)

        # Wait until our builder get's applied
        async_assert(lambda: jk.find_job(job_name).builders)

        # Next, trigger a build
        jb.start_build()
        async_assert(lambda: len(jb.all_builds) == 1)

        # finally, make sure the list or archived artifacts looks correct
        bld = jb.all_builds[0]
        results = bld.artifact_urls

        assert isinstance(results, list)
        assert len(results) == 1
        assert expected_file in results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
