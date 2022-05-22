import pytest
from .utils import async_assert
from pyjen.plugins.gitscm import GitSCM
from pyjen.plugins.freestylejob import FreestyleJob


@pytest.mark.vcr()
@pytest.fixture(scope="class")
def test_builds_with_git(request, jenkins_api):
    """Helper fixture that creates a job with a sample build with Git sources for testing"""
    request.cls.jenkins = jenkins_api
    request.cls.job = jenkins_api.create_job(request.cls.__name__ + "Job", FreestyleJob)
    assert request.cls.job is not None

    expected_url = "https://github.com/TheFriendlyCoder/pyjen.git"
    test_scm = GitSCM.instantiate(expected_url)
    request.cls.job.scm = test_scm

    request.cls.job.quiet_period = 0
    async_assert(lambda: isinstance(request.cls.job.scm, GitSCM))

    request.cls.job.start_build()
    async_assert(lambda: request.cls.job.last_good_build is not None)

    yield

    request.cls.job.delete()

@pytest.mark.usefixtures('test_builds_with_git')
class TestBuildsWithGit(object):
    @pytest.mark.skip(reason="To be fixed")
    def test_get_changeset(self):

        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset is not None

    @pytest.mark.skip(reason="To be fixed")
    def test_get_changeset_scm_type(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset.scm_type == "git"

    @pytest.mark.skip(reason="To be fixed")
    def test_get_has_no_changes(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert chgset.has_changes is False

    @pytest.mark.skip(reason="To be fixed")
    def test_get_has_no_affected_items(self):
        bld = self.job.last_good_build
        chgset = bld.changeset
        assert isinstance(chgset.affected_items, list)
        assert len(chgset.affected_items) == 0
