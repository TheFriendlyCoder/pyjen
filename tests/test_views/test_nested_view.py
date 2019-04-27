from pyjen.jenkins import Jenkins
import pytest
from pyjen.plugins.nestedview import NestedView
from ..utils import clean_view


def test_create_parent_nested_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_create_parent_nested_view"
    v = jk.create_view(expected_view_name, "hudson.plugins.nested_view.NestedView")
    assert v is not None
    with clean_view(v):
        assert isinstance(v, NestedView)
        assert v.name == expected_view_name


def test_create_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_create_sub_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        expected_view_name = "test_create_sub_view1"
        child = parent.create_view(expected_view_name, "hudson.model.ListView")
        assert child is not None
        with clean_view(child):
            assert child.name == expected_view_name


def test_nested_views_empty(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_all_nested_views_empty", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        result = parent.views
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


def test_find_non_existent_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_find_non_existent_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        result = parent.find_view("FindViewDoesNotExist")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


def test_find_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_find_sub_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        expected_view_name = "test_find_sub_view1"
        child = parent.create_view(expected_view_name, "hudson.model.ListView")
        assert child is not None
        with clean_view(child):
            result = parent.find_view(expected_view_name)
            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].name == child.name


def test_find_nested_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_find_nested_sub_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        child1 = parent.create_view("test_find_nested_sub_view1", "hudson.plugins.nested_view.NestedView")

        with clean_view(child1):
            expected_view_name = "test_find_nested_sub_view2"
            child2 = child1.create_view(expected_view_name, "hudson.model.ListView")
            assert child2 is not None
            with clean_view(child2):
                result = parent.find_view(expected_view_name)
                assert result is not None
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0].name == expected_view_name


def test_find_multiple_nested_sub_views(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent1 = jk.create_view("test_find_multiple_nested_sub_views_parent1", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent1):
        parent2 = parent1.create_view("test_find_multiple_nested_sub_views_parent2", "hudson.plugins.nested_view.NestedView")
        with clean_view(parent2):
            expected_view_name = "test_find_multiple_nested_sub_views_child"

            # Views in Jenkins must be unique within the same parent view, but
            # nested views may contain sub-views with the same name as their
            # ancestors / siblings. So we create 2 views with the same name in
            # each of our parent views to make sure they get resolved correctly
            child1 = parent1.create_view(expected_view_name, "hudson.model.ListView")
            assert child1 is not None
            with clean_view(child1):
                child2 = parent2.create_view(expected_view_name, "hudson.model.ListView")
                assert child2 is not None
                with clean_view(child2):

                    results = parent1.find_view(expected_view_name)
                    assert results is not None
                    assert isinstance(results, list)
                    assert len(results) == 2
                    assert results[0].name == expected_view_name
                    assert results[1].name == expected_view_name


def test_all_views_empty(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.create_view("test_all_views_empty", "hudson.plugins.nested_view.NestedView")
    with clean_view(v):
        result = v.all_views
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


def test_all_views_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_all_views_sub_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        expected_view_name = "test_all_views_sub_view1"
        child = parent.create_view(expected_view_name, "hudson.model.ListView")
        assert child is not None
        with clean_view(child):
            result = parent.all_views
            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].name == child.name


def test_all_views_nested_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_all_views_nested_sub_view_parent", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        expected_view_name1 = "test_all_views_nested_sub_view_child1"
        child1 = parent.create_view(expected_view_name1, "hudson.plugins.nested_view.NestedView")

        with clean_view(child1):
            expected_view_name2 = "test_all_views_nested_sub_view_child2"
            child2 = child1.create_view(expected_view_name2, "hudson.model.ListView")
            assert child2 is not None
            with clean_view(child2):
                results = parent.all_views
                assert results is not None
                assert isinstance(results, list)
                assert len(results) == 2
                assert results[0].name in [expected_view_name1, expected_view_name2]
                assert results[1].name in [expected_view_name1, expected_view_name2]


def test_clone_sub_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_clone_sub_view_parent", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        child1 = parent.create_view("test_clone_sub_view_child1", "hudson.model.ListView")

        with clean_view(child1):
            expected_view_name = "test_clone_sub_view_child2"
            child2 = parent.clone_view(child1, expected_view_name)
            assert child2 is not None
            with clean_view(child2):
                assert child2.name == expected_view_name
                assert isinstance(child2, type(child1))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
