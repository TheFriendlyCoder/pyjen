from pyjen.view import View
from pyjen.job import Job
import pytest
from mock import MagicMock

fake_job_url = "http://localhost:8080/MyView/Job1"
fake_job_name = 'Job1'
fake_config_xml = """<hudson.model.AllView>
    <name>All</name>
    <filterExecutors>false</filterExecutors>
    <filterQueue>false</filterQueue>
    <properties class="hudson.model.View$PropertyList"/>
</hudson.model.AllView>"""

fake_view_data = {
    'name': 'MyView',
    'jobs': [{'url': fake_job_url, 'name': fake_job_name}]
}

@pytest.fixture
def patch_view_api(monkeypatch):
    mock_api_data = MagicMock()
    mock_api_data.return_value = fake_view_data

    mock_api_text = MagicMock()
    mock_api_text.return_value = fake_config_xml

    monkeypatch.setattr(View, "get_api_data", mock_api_data)
    monkeypatch.setattr(View, "get_text", mock_api_text)


def get_mock_api_data(field, data):
    tmp_data = fake_view_data.copy()
    tmp_data[field] = data
    mock_api_data = MagicMock()
    mock_api_data.return_value = tmp_data
    return mock_api_data


def test_get_name(patch_view_api):
    v = View("http://localhost:8080/MyView")
    assert v.name == fake_view_data['name']


def test_get_jobs(patch_view_api):
    v = View("http://localhost:8080/MyView")
    jobs = v.jobs

    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)
    assert jobs[0].url == fake_job_url + "/"        # the API should append a trailing slash to the URL


def test_get_jobs_no_jobs(monkeypatch):
    monkeypatch.setattr(View, "get_api_data", get_mock_api_data('jobs', []))

    v = View("http://localhost:8080/MyView")
    jobs = v.jobs

    assert len(jobs) == 0


def test_get_config_xml(patch_view_api):
    v = View("http://localhost:8080/MyVew")
    assert v.config_xml == fake_config_xml


def test_delete_view(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(View, "post", mock_post)

    view_url = "http://localhost:8080/MyView"
    v = View(view_url)
    v.delete()

    mock_post.assert_called_once_with(view_url + "/doDelete")


def test_set_config_xml(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(View, "post", mock_post)
    view_url = "http://localhost:8080/MyView"
    v = View(view_url)
    v.config_xml = fake_config_xml

    assert mock_post.call_count == 1
    assert len(mock_post.call_args) == 2
    assert mock_post.call_args[0][0] == view_url + "/config.xml"
    assert 'data' in mock_post.call_args[0][1]
    assert mock_post.call_args[0][1]['data'] == fake_config_xml


def test_delete_all_jobs(monkeypatch):
    patch_view_api(monkeypatch)

    mock_job_post = MagicMock()
    monkeypatch.setattr(Job, 'post', mock_job_post)

    v = View("http://localhost:8080/MyView")
    v.delete_all_jobs()

    mock_job_post.assert_called_once_with(fake_job_url + "/doDelete")


def test_disable_all_jobs(monkeypatch):
    patch_view_api(monkeypatch)

    mock_job_post = MagicMock()
    monkeypatch.setattr(Job, 'post', mock_job_post)

    v = View("http://localhost:8080/MyView")
    v.disable_all_jobs()

    mock_job_post.assert_called_once_with(fake_job_url + "/disable")


def test_enable_all_jobs(monkeypatch):
    patch_view_api(monkeypatch)

    mock_job_post = MagicMock()
    monkeypatch.setattr(Job, 'post', mock_job_post)

    v = View("http://localhost:8080/MyView")
    v.enable_all_jobs()

    mock_job_post.assert_called_once_with(fake_job_url + "/enable")
    v.enable_all_jobs()


def test_view_metrics(monkeypatch):
    mock_view_api_data = MagicMock()
    fake_data = fake_view_data.copy()
    fake_data['jobs'] = [
        {'url': 'http://fake/job/a'},
        {'url': 'http://fake/job/b'},
        {'url': 'http://fake/job/c'},
        {'url': 'http://fake/job/d'},
        {'url': 'http://fake/job/e'}
    ]
    mock_view_api_data.return_value = fake_data
    monkeypatch.setattr(View, 'get_api_data', mock_view_api_data)

    mock_job_api_data = MagicMock()
    mock_job_api_data.side_effect = [
        {'color': 'blue'}, {'color': 'blue'}, {'color': 'blue'},
        {'color': 'red'},
        {'color': 'yellow'}, {'color': 'yellow'}, {'color': 'yellow'},
        {'color': 'disabled'}, {'color': 'disabled'},
        {'color': 'red'}
    ]
    monkeypatch.setattr(Job, 'get_api_data', mock_job_api_data)
    v = View("http://localhost:8080/MyView")
    result = v.view_metrics

    assert result['broken_jobs_count'] == 2
    assert result['disabled_jobs_count'] == 1
    assert result['unstable_jobs_count'] == 1

    for broken_job in result['broken_jobs']:
        assert broken_job.url in ['http://fake/job/b/', 'http://fake/job/e/']

    assert result['unstable_jobs'][0].url == 'http://fake/job/c/'

    assert result['disabled_jobs'][0].url == 'http://fake/job/d/'


def test_clone_all_jobs(monkeypatch):
    patch_view_api(monkeypatch)
    mock_job_post = MagicMock()
    monkeypatch.setattr(Job, 'post', mock_job_post)
    monkeypatch.setattr(Job, 'get_api_data', lambda s: {'name': fake_job_name})

    new_job_name = "NewJob"
    jenkins_url = "http://localhost:8080/"
    v = View(jenkins_url + "MyView")
    v.clone_all_jobs(fake_job_name, new_job_name)

    assert mock_job_post.call_count > 1   # The post method is called twice but we only care about the first one
    assert len(mock_job_post.call_args_list[0]) == 2    # should have 2 arguments on the first call

    # 1st arg should e the URL for cloning a job
    assert mock_job_post.call_args_list[0][0][0] == jenkins_url + "createItem"

    # 2nd arg should be a dictionary containing details of the copy operation
    assert mock_job_post.call_args_list[0][0][1]['params']['name'] == new_job_name
    assert mock_job_post.call_args_list[0][0][1]['params']['mode'] == 'copy'
    assert mock_job_post.call_args_list[0][0][1]['params']['from'] == fake_job_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
