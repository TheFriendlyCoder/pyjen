from pyjen.utils.datarequester import *
import unittest
import pytest


class DataRequesterTests(unittest.TestCase):
    def test_basic_constructon(self):
        expected_url = "http://localhost:8080/"

        req = DataRequester(expected_url)

        self.assertEqual(req.url, expected_url)
        self.assertIsNone(req.credentials)

    def test_url_slash(self):
        url = "http://localhost:8080"

        req = DataRequester(url)

        self.assertEqual(req.url, url + "/")
        self.assertIsNone(req.credentials)

    def test_clone(self):
        expected_url = "http://localhost:8080/"
        expected_creds = ("MyUser", "MyPassword")
        req = DataRequester(expected_url)
        req.credentials = expected_creds

        copy = req.clone()

        self.assertEqual(copy.url, expected_url)
        self.assertEqual(copy.credentials, expected_creds)

    def test_clone_new_url(self):
        expected_url = "http://localhost:8080/job/job1/"
        expected_creds = ("MyUser", "MyPassword")
        req = DataRequester("http://localhost:8080/")
        req.credentials = expected_creds

        copy = req.clone(expected_url)

        self.assertEqual(copy.url, expected_url)
        self.assertEqual(copy.credentials, expected_creds)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
