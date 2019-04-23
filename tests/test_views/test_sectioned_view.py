from pyjen.jenkins import Jenkins
import pytest
from pyjen.plugins.sectionedview import SectionedView
from ..utils import clean_view


def test_create_sectioned_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_create_sectioned_view"
    v = jk.create_view(expected_view_name, SectionedView)
    assert v is not None
    with clean_view(v):
        assert isinstance(v, SectionedView)
        assert v.name == expected_view_name


def test_get_sections_empty(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_get_sections_empty"
    v = jk.create_view(expected_view_name, SectionedView)
    with clean_view(v):
        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


def test_add_list_section(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.create_view("test_add_list_section", SectionedView)
    with clean_view(v):
        expected_name = "MyNewSection"
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", expected_name)

        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        tmp = result[0]
        assert tmp.name == expected_name


def test_list_section_no_regex(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.create_view("test_list_section_no_regex",SectionedView)
    with clean_view(v):
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", "MyNewSection")

        section = v.sections[0]
        assert section.include_regex == ""


@pytest.mark.skip("TODO: Fix regex setter on SectionedView class")
def test_list_section_set_regex(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.create_view("test_list_section_set_regex", SectionedView)
    with clean_view(v):
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", "MyNewSection")

        section = v.sections[0]
        expected_regex = "release.*"
        section.include_regex = expected_regex
        assert v.sections[0].include_regex == expected_regex


def test_add_text_section(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    v = jk.create_view("test_add_text_section", SectionedView)
    with clean_view(v):
        expected_name = "MyNewSection"
        v.add_section("hudson.plugins.sectioned_view.TextSection", expected_name)

        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == expected_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
