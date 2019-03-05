from pyjen.utils.datarequester import *
import pytest


def test_basic_constructon():
    expected_url = "http://localhost:8080/"

    req = DataRequester(expected_url)

    assert req.url == expected_url
    assert req.credentials is None


def test_url_slash():
    url = "http://localhost:8080"

    req = DataRequester(url)

    assert req.url ==  url + "/"
    assert req.credentials is None


def test_clone():
    expected_url = "http://localhost:8080/"
    expected_creds = ("MyUser", "MyPassword")
    req = DataRequester(expected_url)
    req.credentials = expected_creds

    copy = req.clone()

    assert copy.url == expected_url
    assert copy.credentials == expected_creds


def test_clone_new_url():
    expected_url = "http://localhost:8080/job/job1/"
    expected_creds = ("MyUser", "MyPassword")
    req = DataRequester("http://localhost:8080/")
    req.credentials = expected_creds

    copy = req.clone(expected_url)

    assert copy.url == expected_url
    assert copy.credentials == expected_creds


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
