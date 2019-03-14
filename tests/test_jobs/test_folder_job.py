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
        jb2 = jb.create_job(expected_name, "hudson.model.FreeStyleProject")
        assert jb2 is not None
        with clean_job(jb2):
            assert jb2.name == expected_name


def test_folder_find_job_not_found(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_folder_find_job_not_found", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        jb2 = jb.find_job("SubJobThatDoesntExist")
        assert jb2 is None


def test_folder_find_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_folder_find_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        expected_job_name = "test_folder_find_job2"
        jb2 = jb.create_job(expected_job_name, "hudson.model.FreeStyleProject")
        with clean_job(jb2):
            result = jb.find_job(expected_job_name)
            assert result is not None
            assert result.name == expected_job_name
            assert isinstance(result, type(jb2))


def test_clone_job_in_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job_in_folder_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        jb2 = jb.create_job("test_clone_job_in_folder_job2", "hudson.model.FreeStyleProject")
        with clean_job(jb2):
            expected_name = "test_clone_job_in_folder_job3"
            jb3 = jb.clone_job(jb2, expected_name)
            assert jb3 is not None
            with clean_job(jb3):
                assert jb3.name == expected_name
                assert jb3.is_disabled
                assert jb2.is_disabled is False


def test_clone_enabled_job_in_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_enabled_job_in_folder_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        jb2 = jb.create_job("test_clone_enabled_job_in_folder_job2", "hudson.model.FreeStyleProject")
        with clean_job(jb2):
            expected_name = "test_clone_enabled_job_in_folder_job3"
            jb3 = jb.clone_job(jb2, expected_name, False)
            assert jb3 is not None
            with clean_job(jb3):
                assert jb3.name == expected_name
                assert jb3.is_disabled is False
                assert jb2.is_disabled is False

def test_move_job_to_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_move_job_to_folder_job", "com.cloudbees.hudson.plugins.folder.Folder")
    with clean_job(jb):
        expected_job_name = "test_move_job_to_folder_job2"
        jb2 = jk.create_job(expected_job_name, "hudson.model.FreeStyleProject")
        # we need to be careful while we perform the move operation. If the
        # move fails we need to make sure to clean up the original job, but
        # if the move succeeds the original job becomes invalidated so we
        # can simply ignore it
        try:
            jb3 = jb.move_job(jb2)
            assert jk.find_job(expected_job_name) is None
        except:
            jb2.delete()
            raise

        # Once we get here we are relatively certain the move has completed
        # successfully. Do some further validation to make sure the move
        # worked as expected
        with clean_job(jb3):
            assert jb3.name == expected_job_name
            assert isinstance(jb3, type(jb2))

            temp = jb.find_job(expected_job_name)
            assert temp is not None
            assert temp.name == expected_job_name
            assert isinstance(temp, type(jb2))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
