from pyjen.jenkins import Jenkins


def test_find_user(jenkins_api):
    user = jenkins_api.find_user("admin")
    assert user is not None
    assert user.full_name == "admin"


def test_get_no_description(jenkins_api):
    user = jenkins_api.find_user("admin")
    result = user.description

    assert result is not None
    assert isinstance(result, str)
    assert result == ''


def test_get_user_id(jenkins_api):
    user = jenkins_api.find_user("admin")
    result = user.user_id

    assert result is not None
    assert result == "admin"


def test_get_no_email(jenkins_api):
    user = jenkins_api.find_user("admin")
    result = user.email

    assert result is None


def test_create_api_token(jenkins_env, jenkins_api):
    user = jenkins_api.find_user("admin")

    token = user.create_api_token("test_create_api_token")
    assert token is not None
    assert isinstance(token, str)

    jk = Jenkins.basic_auth(jenkins_env["url"], (jenkins_env["admin_user"], token))
    assert jk.version == jenkins_api.version
