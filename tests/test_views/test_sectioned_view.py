import pytest
from pyjen.plugins.sectionedview import SectionedView
from ..utils import clean_view


@pytest.mark.vcr()
def test_create_sectioned_view(jenkins_api):
    expected_view_name = "test_create_sectioned_view"
    v = jenkins_api.create_view(expected_view_name, SectionedView)
    assert v is not None
    with clean_view(v):
        assert isinstance(v, SectionedView)
        assert v.name == expected_view_name


@pytest.mark.vcr()
def test_get_sections_empty(jenkins_api):
    expected_view_name = "test_get_sections_empty"
    v = jenkins_api.create_view(expected_view_name, SectionedView)
    with clean_view(v):
        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0


@pytest.mark.vcr()
def test_add_list_section(jenkins_api):
    v = jenkins_api.create_view("test_add_list_section", SectionedView)
    with clean_view(v):
        expected_name = "MyNewSection"
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", expected_name)

        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        tmp = result[0]
        assert tmp.name == expected_name


@pytest.mark.vcr()
def test_list_section_no_regex(jenkins_api):
    v = jenkins_api.create_view("test_list_section_no_regex", SectionedView)
    with clean_view(v):
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", "MyNewSection")

        section = v.sections[0]
        assert section.include_regex == ""


@pytest.mark.vcr()
def test_list_section_set_regex(jenkins_api):
    v = jenkins_api.create_view("test_list_section_set_regex", SectionedView)
    with clean_view(v):
        v.add_section("hudson.plugins.sectioned_view.ListViewSection", "MyNewSection")

        section = v.sections[0]
        expected_regex = "release.*"
        section.include_regex = expected_regex
        assert v.sections[0].include_regex == expected_regex


@pytest.mark.vcr()
def test_add_text_section(jenkins_api):
    v = jenkins_api.create_view("test_add_text_section", SectionedView)
    with clean_view(v):
        expected_name = "MyNewSection"
        v.add_section("hudson.plugins.sectioned_view.TextSection", expected_name)

        result = v.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == expected_name


@pytest.mark.vcr()
def test_rename_view(jenkins_api):
    original_view_name = "test_rename_view"
    v = jenkins_api.create_view(original_view_name, SectionedView)
    try:
        expected_section_name = "MyNewSection"
        v.add_section("hudson.plugins.sectioned_view.TextSection", expected_section_name)

        expected_view_name = "test_rename_view2"
        v.rename(expected_view_name)
        assert jenkins_api.find_view(original_view_name) is None
    finally:
        tmp = jenkins_api.find_view(original_view_name)
        if tmp:
            tmp.delete()

    with clean_view(v):
        assert v.name == expected_view_name

        tmp_view = jenkins_api.find_view(expected_view_name)
        assert tmp_view is not None
        assert tmp_view.name == expected_view_name

        result = tmp_view.sections

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == expected_section_name


@pytest.mark.vcr()
def test_clone_view(jenkins_api):
    original_view_name = "test_clone_view"
    vw1 = jenkins_api.create_view(original_view_name, SectionedView)

    with clean_view(vw1):
        expected_section_name = "MyNewSection"
        vw1.add_section("hudson.plugins.sectioned_view.TextSection", expected_section_name)

        expected_view_name = "test_clone_view2"
        vw2 = vw1.clone(expected_view_name)
        assert vw2 is not None
        with clean_view(vw2):

            tmp_view = jenkins_api.find_view(expected_view_name)
            assert tmp_view is not None
            assert tmp_view.name == expected_view_name

            result = tmp_view.sections

            assert result is not None
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].name == expected_section_name
