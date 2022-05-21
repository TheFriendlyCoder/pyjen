import pytest
from pyjen.plugins.allview import AllView


@pytest.mark.vcr()
def test_find_view(jenkins_api):
    expected_name = "all"
    v = jenkins_api.find_view(expected_name)

    assert isinstance(v, AllView)
