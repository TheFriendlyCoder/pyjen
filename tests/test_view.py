import pytest
from .utils import clean_view, clean_job
from pyjen.plugins.listview import ListView
from pyjen.plugins.freestylejob import FreestyleJob


@pytest.mark.vcr()
def test_delete_view(jenkins_api):
    expected_view_name = "test_delete_view"
    vw = jenkins_api.create_view(expected_view_name, ListView)
    vw.delete()
    assert jenkins_api.find_view(expected_view_name) is None


@pytest.mark.vcr()
def test_get_name(jenkins_api):
    expected_name = "test_get_name_view"
    vw = jenkins_api.create_view(expected_name, ListView)
    with clean_view(vw):
        assert vw.name == expected_name


@pytest.mark.vcr()
def test_get_jobs_no_jobs(jenkins_api):
    vw = jenkins_api.create_view("test_get_jobs_no_jobs_views", ListView)
    with clean_view(vw):
        jobs = vw.jobs
        assert isinstance(jobs, list)
        assert len(jobs) == 0


@pytest.mark.vcr()
def test_get_jobs(jenkins_api):
    expected_job_name = "test_get_jobs_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        vw = jenkins_api.default_view
        all_jobs = vw.jobs
        assert isinstance(all_jobs, list)
        assert len(all_jobs) == 1
        assert all_jobs[0].name == expected_job_name
        assert isinstance(all_jobs[0], type(jb))


@pytest.mark.vcr()
def test_delete_all_jobs(jenkins_api):
    expected_job_name = "test_delete_all_jobs_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)

    try:
        vw = jenkins_api.default_view
        assert len(vw.jobs) == 1
        vw.delete_all_jobs()
        assert len(vw.jobs) == 0
    except:
        # In case our delete operation doesn't complete successfully, we do
        # a manual deletion here to keep our test environment clean
        jb.delete()
        raise


@pytest.mark.vcr()
def test_disable_all_jobs(jenkins_api):
    expected_job_name = "test_disable_all_jobs_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)

    with clean_job(jb):
        vw = jenkins_api.default_view
        vw.disable_all_jobs()
        assert jb.is_disabled


@pytest.mark.vcr()
def test_enable_all_jobs(jenkins_api):
    expected_job_name = "test_enable_all_jobs_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)

    with clean_job(jb):
        vw = jenkins_api.default_view
        jb.disable()
        vw.enable_all_jobs()
        assert jb.is_disabled is False


@pytest.mark.vcr()
def test_get_config_xml(jenkins_api):
    assert jenkins_api.default_view.config_xml


@pytest.mark.vcr()
def test_get_view_metrics(jenkins_api):
    expected_job_name = "test_get_view_metrics_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        jb.disable()
        result = jenkins_api.default_view.view_metrics
        expected_keys = [
            'unstable_jobs',
            'unstable_jobs_count',
            'broken_jobs_count',
            'disabled_jobs',
            'disabled_jobs_count',
            'broken_jobs'
        ]

        for cur_key in expected_keys:
            assert cur_key in result.keys()
        assert result['broken_jobs_count'] == 0
        assert result['disabled_jobs_count'] == 1
        assert result['unstable_jobs_count'] == 0
        assert isinstance(result['disabled_jobs'], list)
        assert len(result['disabled_jobs']) == 1
        assert result['disabled_jobs'][0].name == expected_job_name


@pytest.mark.vcr()
def test_clone_view(jenkins_api):
    vw = jenkins_api.create_view("test_clone_view1", ListView)
    with clean_view(vw):
        expected_name = "test_clone_view2"
        vw2 = vw.clone(expected_name)
        assert vw2 is not None
        with clean_view(vw2):
            assert vw2.name == expected_name
            assert isinstance(vw2, type(vw))


@pytest.mark.vcr()
def test_rename_view(jenkins_api):
    original_view_name = "test_rename_view1"
    vw = jenkins_api.create_view(original_view_name, ListView)
    try:
        expected_name = "test_rename_view2"
        vw.rename(expected_name)
        assert jenkins_api.find_view(original_view_name) is None
    finally:
        tmp = jenkins_api.find_view(original_view_name)
        if tmp:
            tmp.delete()

    with clean_view(vw):
        assert vw.name == expected_name

        tmp_view = jenkins_api.find_view(expected_name)
        assert tmp_view is not None
        assert tmp_view.name == expected_name
