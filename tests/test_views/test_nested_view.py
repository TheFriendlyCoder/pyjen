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
        source_view_name = "test_clone_sub_view_child1"
        child1 = parent.create_view(source_view_name, "hudson.model.ListView")

        with clean_view(child1):
            expected_view_name = "test_clone_sub_view_child2"
            child2 = child1.clone(expected_view_name)
            assert child2 is not None
            with clean_view(child2):
                assert child2.name == expected_view_name
                assert isinstance(child2, type(child1))


def test_move_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    parent = jk.create_view("test_move_view", "hudson.plugins.nested_view.NestedView")
    with clean_view(parent):
        expected_view_name = "test_move_view_child1"
        original_child = jk.create_view(expected_view_name, "hudson.model.ListView")

        # after we move the view to the new location, the old view becomes
        # invalidated. So here we try and make sure the original view always
        # gets cleaned up even if the test fails, but only until we know
        # the move operation has completed
        try:
            new_child = parent.move_view(original_child)
            assert new_child is not None
        except:
            if original_child:
                original_child.delete()
            raise

        # If we get here we can be fairly certain the old view as been destroyed
        # and the new view has been created. That being the case we need to make
        # sure the new view gets cleaned up when the test finishes
        with clean_view(new_child):
            # Make sure the new child has been created
            assert new_child.name == expected_view_name
            results = parent.views
            assert len(results) == 1
            assert results[0].name == expected_view_name

            # make sure the original view no longer exists in the parent namespace
            assert jk.find_view(expected_view_name) is None

            # Final sanity check to make sure the original view object gets
            # invalidated. We do this by trying to force a call against the
            # REST API using the original API endpoint, and any such requests
            # should fail and raise an exception
            with pytest.raises(Exception):
                original_child.config_xml


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
