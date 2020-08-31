from pyjen.plugins.listview import ListView
from ..utils import clean_view


def test_create_list_view(jenkins_api):
    expected_view_name = "test_create_list_view"
    v = jenkins_api.create_view(expected_view_name, ListView)
    assert v is not None
    with clean_view(v):
        assert isinstance(v, ListView)
        assert v.name == expected_view_name
