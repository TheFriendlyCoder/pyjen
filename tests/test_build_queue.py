import pytest
from mock import MagicMock
from .utils import async_assert, clean_job
from requests.exceptions import HTTPError
from pyjen.jenkins import Jenkins
from pyjen.queue_item import QueueItem
from pyjen.plugins.freestylejob import FreestyleJob


def test_waiting_build_queue(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    queue = jk.build_queue
    jb = jk.create_job("test_waiting_build_queue", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 5
        jb.start_build()
        res = queue.items
        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0].stuck is False
        assert isinstance(res[0].id, int)
        qjob = res[0].job
        assert qjob == jb


def test_out_of_queue(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    queue = jk.build_queue
    jb = jk.create_job("test_waiting_build_queue", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 1
        jb.start_build()

        res = queue.items
        assert isinstance(res, list)
        assert len(res) == 1
        item = res[0]
        assert item.waiting is True
        async_assert(lambda: jb.last_build)
        assert item.waiting is False


def test_cancel_queued_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    queue = jk.build_queue
    jb = jk.create_job("test_cancel_queued_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 10
        jb.start_build()

        res = queue.items
        item = res[0]
        assert item.waiting is True
        item.cancel()
        assert item.waiting is False
        assert item.cancelled is True


def test_get_build_after_queued(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    queue = jk.build_queue
    jb = jk.create_job("test_get_build_after_queued", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 1
        jb.start_build()

        res = queue.items
        item = res[0]
        assert item.build is None
        async_assert(lambda: jb.last_build)

        assert item.build is not None
        assert item.build == jb.last_build


def test_start_build_returned_queue_item(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    queue = jk.build_queue
    jb = jk.create_job("test_start_build_returned_queue_item", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 1
        item = jb.start_build()

        assert item is not None
        assert isinstance(item, QueueItem)
        assert queue.items[0] == item


def test_queue_get_build(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_queue_get_build", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        item = jb.start_build()

        async_assert(lambda: not item.waiting)

        bld = item.build
        assert bld is not None
        assert bld == jb.last_build


def test_is_valid(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_is_valid", FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        item = jb.start_build()

        async_assert(lambda: jb.last_build)

        # Our queue item should remain valid even after it leaves the queue
        assert item.is_valid()


@pytest.mark.skip("Disabling long-running sanity test")
def test_is_not_valid(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    jb = jk.create_job("test_is_not_valid", FreestyleJob)
    from time import sleep
    with clean_job(jb):
        jb.quiet_period = 0
        item = jb.start_build()

        async_assert(lambda: jb.last_build)

        # Apparently Jenkins retains build queue items for 5 minutes
        # so we wait 6 minutes before proceeding
        sleep(360)
        assert not item.is_valid()


def test_getters_from_invalid_queue_item():
    # First we mock an HTTP 404 error response, which is what the Jenkins
    # REST API will return when the endpoint referenced by our queue item
    # no longer exists
    mock_response = MagicMock()
    mock_response.status_code = 404

    # Mock a Jenkins REST API object with the relevant structures used by
    # our queue item
    mock_api = MagicMock()
    mock_api.get_api_data.side_effect = HTTPError(response=mock_response)
    expected_id = 1234
    mock_api.url = "https://jenkins.server/queue/item/" + str(expected_id)

    # Flex our code
    q1 = QueueItem(mock_api)

    # confirm the results
    assert q1.id == expected_id
    assert q1.stuck is None
    assert q1.blocked is None
    assert q1.buildable is None
    assert q1.reason is None
    assert q1.waiting is None
    assert q1.cancelled is None
    assert q1.job is None
    assert q1.build is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
