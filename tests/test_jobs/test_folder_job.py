import pytest
from ..utils import clean_job
from pyjen.jenkins import Jenkins


def test_create_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_folder_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        assert jb is not None


def test_create_folder_job_with_subjob(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_folder_job_with_subjob", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        expected_name = "test_create_folder_job_with_subjob2"
        jb2 = jb.derived_object.create_job(expected_name, "project")
        assert jb2 is not None
        with clean_job(jb2):
            assert jb2.name == expected_name


def test_folder_find_job_not_found(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_folder_find_job_not_found", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        jb2 = jb.derived_object.find_job("SubJobThatDoesntExist")
        assert jb2 is None


@pytest.mark.skip("TODO: Fix job cloning logic to work with folder views")
def test_clone_job_in_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job_in_folder_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        jb2 = jb.derived_object.create_job("test_clone_job_in_folder_job2", "project")
        with clean_job(jb2):
            expected_name = "test_clone_job_in_folder_job3"
            jb3 = jb2.clone(expected_name)
            assert jb3 is not None
            with clean_job(jb3):
                assert jb3.name == expected_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
