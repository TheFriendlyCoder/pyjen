import pytest
from ..utils import clean_job
from pyjen.jenkins import Jenkins
from pyjen.plugins.folderjob import FolderJob
from pyjen.plugins.freestylejob import FreestyleJob


def test_create_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_folder_job", FolderJob)
    with clean_job(jb):
        assert jb is not None


def test_create_folder_job_with_subjob(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_create_folder_job_with_subjob", FolderJob)
    with clean_job(jb):
        expected_name = "test_create_folder_job_with_subjob2"
        jb2 = jb.create_job(expected_name, FreestyleJob)
        assert jb2 is not None
        with clean_job(jb2):
            assert jb2.name == expected_name


def test_folder_find_job_not_found(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_folder_find_job_not_found", FolderJob)
    with clean_job(jb):
        jb2 = jb.find_job("SubJobThatDoesntExist")
        assert jb2 is None


def test_folder_find_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_folder_find_job", FolderJob)
    with clean_job(jb):
        expected_job_name = "test_folder_find_job2"
        jb2 = jb.create_job(expected_job_name, FreestyleJob)
        with clean_job(jb2):
            result = jb.find_job(expected_job_name)
            assert result is not None
            assert result.name == expected_job_name
            assert isinstance(result, type(jb2))


def test_clone_job_in_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_job_in_folder_job", FolderJob)
    with clean_job(jb):
        jb2 = jb.create_job("test_clone_job_in_folder_job2", FreestyleJob)
        with clean_job(jb2):
            expected_name = "test_clone_job_in_folder_job3"
            jb3 = jb2.clone(expected_name)
            assert jb3 is not None
            with clean_job(jb3):
                assert jb3.name == expected_name
                assert jb3.is_disabled
                assert jb2.is_disabled is False


def test_clone_enabled_job_in_folder_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_clone_enabled_job_in_folder_job", FolderJob)
    with clean_job(jb):
        jb2 = jb.create_job("test_clone_enabled_job_in_folder_job2", FreestyleJob)
        with clean_job(jb2):
            expected_name = "test_clone_enabled_job_in_folder_job3"
            jb3 = jb2.clone(expected_name, False)
            assert jb3 is not None
            with clean_job(jb3):
                assert jb3.name == expected_name
                assert jb3.is_disabled is False
                assert jb2.is_disabled is False


def test_rename_job(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_job("test_rename_job_parent", FolderJob)
    with clean_job(parent):
        original_job_name = "test_rename_job1"
        new_job_name = "test_rename_job2"
        jb = parent.create_job(original_job_name, FreestyleJob)
        try:
            jb.rename(new_job_name)
            assert parent.find_job(original_job_name) is None
            jb_copy = parent.find_job(new_job_name)
            assert jb_copy is not None
            assert jb.name == new_job_name
            assert jb_copy == jb
        finally:
            tmp = parent.find_job(original_job_name)
            if tmp:
                tmp.delete()

            tmp = parent.find_job(new_job_name)
            if tmp:
                tmp.delete()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
