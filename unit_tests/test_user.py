from pyjen.user import User
import pytest

sample_email = "john.doe@foo.bar.com"

# This dictionary represents a "typical" dataset returned by the Jenkins REST API
# when querying information about a user. This is used to fake output from the REST API
# for tests below.
fake_user_data = {
    "id": "myuserid",
    "fullName": "John Doe",
    "description": "Here is where I'd describe myself",
    "property": [{"address": sample_email}]
}


@pytest.fixture
def patch_user_api(monkeypatch):
    monkeypatch.setattr(User, "get_api_data", lambda s: fake_user_data)


def test_get_user_id(patch_user_api):
    u = User("http://localhost:8080/user/johnd")

    assert u.user_id == fake_user_data["id"]


def test_get_full_username(patch_user_api):
    u = User("http://localhost:8080/user/johnd")

    assert u.full_name == fake_user_data["fullName"]


def test_get_description(patch_user_api):
    u = User("http://localhost:8080/user/johnd")

    assert u.description == fake_user_data["description"]


def test_get_no_description(monkeypatch):
    tmp_data = fake_user_data.copy()
    tmp_data["description"] = None
    monkeypatch.setattr(User, "get_api_data", lambda x: tmp_data)

    u = User("http://localhost:8080/user/johnd")

    assert u.description == ""


def test_get_email(patch_user_api):

    u = User("http://localhost:8080/user/johnd")

    assert u.email == sample_email


def test_get_no_email(monkeypatch):
    tmp_data = fake_user_data.copy()
    del tmp_data['property'][0]['address']
    monkeypatch.setattr(User, "get_api_data", lambda x: tmp_data)

    u = User("http://localhost:8080/user/johnd")
    assert u.email is None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
