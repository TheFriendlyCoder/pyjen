import time
from datetime import datetime, timedelta
from pyjen.build import Build
import pytest

epoch_time = time.time()
artifact_filename = "MyFile.txt"
changeset_message = "Here's my commit message"

# This dictionary represents a "typical" dataset returned by the Jenkins REST API
# when querying information about a build. This is used to fake output from the REST API
# for tests below.
fake_build_data = {
    "number": 3,
    "timestamp": epoch_time * 1000,  # Jenkins stores timestamps in milliseconds instead of seconds
    "building": True,
    "result": "SUCCESS",
    "description": "Description of my build",
    "id": 3,
    "artifacts": [{"fileName": artifact_filename}],
    "changeSet": {
        "items": [
            {"msg": changeset_message}
            ],
        "kind": "git"
    }
}

fake_build_text = {
    "/consoleText": "Here is my console text"
}

@pytest.fixture
def patch_build_api(monkeypatch):
    monkeypatch.setattr(Build, "get_api_data", lambda s: fake_build_data)
    monkeypatch.setattr(Build, "get_text", lambda s, x: fake_build_text[x])


def test_build_number(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.number == fake_build_data['number']


def test_start_time(patch_build_api):
    expected_time = datetime.fromtimestamp(epoch_time)
    bld = Build('http://localhost:8080/job/MyJob/3')

    # NOTE: Here we give our assertion some wiggle room to avoid superfluous test failures caused by rounding
    #       errors that occasionally happen when converting epoch timestamps to datetimes.
    assert bld.start_time - expected_time < timedelta(seconds=1)


def test_is_building(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.is_building is True


def test_console_text(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.console_output == fake_build_text['/consoleText']


def test_build_result(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.result == fake_build_data['result']


def test_build_description(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.description == fake_build_data['description']


def test_build_no_description(monkeypatch):
    tmp_data = fake_build_data.copy()
    tmp_data['description'] = None

    monkeypatch.setattr(Build, "get_api_data", lambda x: tmp_data)
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.description == ''


def test_build_id(patch_build_api):
    bld = Build('http://localhost:8080/job/MyJob/3')
    assert bld.id == fake_build_data['id']


def test_build_artifacts(patch_build_api):
    bld_url = 'http://localhost:8080/job/MyJob/3'
    bld = Build(bld_url)

    artifacts = bld.artifact_urls
    assert len(artifacts) == 1
    assert artifacts[0] == bld_url + "/artifact/" + artifact_filename


def test_build_equality(monkeypatch):
    bld1 = Build('http://localhost:8080/job/MyJob/3')
    monkeypatch.setattr(bld1, "get_api_data", lambda: fake_build_data)
    bld2 = Build('http://localhost:8080/view/MyView/job/MyJob/3')
    monkeypatch.setattr(bld2, "get_api_data", lambda: fake_build_data)

    assert bld1 == bld2
    assert not bld1 != bld2


def test_build_inequality(monkeypatch):
    bld1 = Build('http://localhost:8080/job/MyJob/3')
    monkeypatch.setattr(bld1, "get_api_data", lambda: fake_build_data)

    # Confirm that 2 builds with different IDs compare as different
    bld2 = Build('http://localhost:8080/view/MyView/job/MyJob/3')
    tmp_data = fake_build_data.copy()
    tmp_data['id'] = 1
    monkeypatch.setattr(bld2, "get_api_data", lambda: tmp_data)

    assert bld1 != bld2
    assert not bld1 == bld2

    # Confirm that 2 builds with different build numbers compare as different
    tmp_data = fake_build_data.copy()
    tmp_data['number'] = 1
    monkeypatch.setattr(bld2, "get_api_data", lambda: tmp_data)

    assert bld1 != bld2
    assert not bld1 == bld2

    # Confirm that comparisons between unrelated objects result in differences
    bld2 = dict()

    assert bld1 != bld2
    assert not bld1 == bld2


def test_build_changesets(patch_build_api):

    bld1 = Build('http://localhost:8080/job/MyJob/3')
    changes = bld1.changeset

    assert changes.has_changes is True
    assert changes.scm_type == "git"
    assert len(changes.affected_items) == 1
    assert changes.affected_items[0].message == changeset_message

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
