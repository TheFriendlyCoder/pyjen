from pyjen.plugins.myview import MyView
from ..utils import clean_view


def test_create_my_view(jenkins_api):
    expected_view_name = "test_create_my_view"
    v = jenkins_api.create_view(expected_view_name, MyView)
    assert v is not None
    with clean_view(v):
        assert isinstance(v, MyView)
        assert v.name == expected_view_name
