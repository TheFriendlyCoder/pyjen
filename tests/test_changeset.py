import pytest


@pytest.mark.usefixtures('test_builds_with_git')
class TestBuildsWithGit(object):
    def test_get_changeset(self):

        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset is not None

    @pytest.mark.skip(reason="To be fixed")
    def test_get_changeset_scm_type(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset.scm_type == "git"

    def test_get_has_no_changes(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset.has_changes is False

    def test_get_has_no_affected_items(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert isinstance(chgset.affected_items, list)
        assert len(chgset.affected_items) == 0
