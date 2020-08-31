from pyjen.plugins.allview import AllView


def test_find_view(jenkins_api):
    expected_name = "all"
    v = jenkins_api.find_view(expected_name)

    assert isinstance(v, AllView)
