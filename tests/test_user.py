from pyjen.jenkins import Jenkins
import pytest


def test_find_user(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user("admin")
    assert user is not None
    assert user.full_name == "admin"


def test_get_no_description(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user("admin")
    result = user.description

    assert result is not None
    assert isinstance(result, str)
    assert result == ''


def test_get_user_id(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user("admin")
    result = user.user_id

    assert result is not None
    assert result == "admin"


def test_get_no_email(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    user = jk.find_user("admin")
    result = user.email

    assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
