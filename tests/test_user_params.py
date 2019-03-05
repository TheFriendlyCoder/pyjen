from pyjen.utils.user_params import JenkinsConfigParser
from pyjen.exceptions import InvalidUserParamsError
import pytest
import os
import platform
from six import StringIO


def test_get_default_configfiles():
    default_config_files = JenkinsConfigParser.get_default_configfiles()

    # Currently we look in 2 locations for config files
    assert len(default_config_files) == 2

    # The least privileged location should be the users home folder
    assert default_config_files[0].startswith(os.path.join(os.path.expanduser("~")))

    # the next most privileged location is the local working folder
    assert default_config_files[1].startswith(os.getcwd())

    # In any case, each path must point to the expected config file name
    if platform.system() == "Windows":
        expected_filename = "pyjen.cfg"
    else:
        expected_filename = ".pyjen"
    for filename in default_config_files:
        assert filename.endswith(expected_filename)


def test_get_credentials_empty_configuration():
    test_obj = JenkinsConfigParser()
    sample_config=StringIO("")
    test_obj.readfp(sample_config)

    assert test_obj.get_credentials("http://localhost:8080") is None


def test_empty_section():
    test_url = "http://localhost:8080"
    sample_config=StringIO("[http://localhost:8080]")
    test_obj = JenkinsConfigParser()
    test_obj.readfp(sample_config)

    assert test_obj.get_credentials(test_url) is None


def test_get_credentials_anonymous():
    test_url = "http://localhost:8080"
    sample_config=StringIO("""[http://localhost:8080]
username=
password=
""")
    test_obj = JenkinsConfigParser()
    test_obj.readfp(sample_config)

    assert test_obj.get_credentials(test_url) is None


def test_get_credentials():
    test_url = "http://localhost:8080"
    expected_username = "jdoe"
    expected_password = "Password123"

    sample_config=StringIO("""[http://localhost:8080]
username=jdoe
password=Password123
""")
    test_obj = JenkinsConfigParser()
    test_obj.readfp(sample_config)

    actual_credentials = test_obj.get_credentials(test_url)
    assert actual_credentials[0] == expected_username
    assert actual_credentials[1] == expected_password


def test_get_credentials_no_username():
    test_url = "http://localhost:8080"

    sample_config=StringIO("""[http://localhost:8080]
password=Password123
""")
    test_obj = JenkinsConfigParser()
    test_obj.readfp(sample_config)

    with pytest.raises(InvalidUserParamsError):
        test_obj.get_credentials(test_url)


def test_get_credentials_no_password():
    test_url = "http://localhost:8080"

    sample_config=StringIO("""[http://localhost:8080]
username=jdoe
""")
    test_obj = JenkinsConfigParser()
    test_obj.readfp(sample_config)

    with pytest.raises(InvalidUserParamsError):
        test_obj.get_credentials(test_url)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
