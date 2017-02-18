import time
from mock import MagicMock
import pytest
from pyjen.node import Node

# This dictionary represents a "typical" dataset returned by the Jenkins REST API
# when querying information about a node. This is used to fake output from the REST API
# for tests below.
fake_node_data = {
    "displayName": "agent1",
    "offline": True,
    'idle': True
}


@pytest.fixture
def patch_node_api(monkeypatch):
    monkeypatch.setattr(Node, "get_api_data", lambda s: fake_node_data)


def test_get_name(patch_node_api):
    n = Node("http://localhost:8080/computer/agent1")
    assert n.name == fake_node_data['displayName']


def test_is_offline(patch_node_api):
    n = Node("http://localhost:8080/computer/agent1")

    assert n.is_offline is True


def test_toggle_offline(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Node, "post", mock_post)
    n = Node("http://localhost:8080/computer/agent1")
    n.toggle_offline()

    mock_post.assert_called_once_with("/toggleOffline")


def test_toggle_offline_with_message(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Node, "post", mock_post)

    n = Node("http://localhost:8080/computer/agent1")
    offline_message = "Description"
    n.toggle_offline(offline_message)

    mock_post.assert_called_once_with("/toggleOffline?offlineMessage=" + offline_message)


def test_toggle_offline_with_message_with_spaces(monkeypatch):
    mock_post = MagicMock()
    monkeypatch.setattr(Node, "post", mock_post)

    n = Node("http://localhost:8080/computer/agent1")
    offline_message = "Descriptive text goes here"
    n.toggle_offline(offline_message)

    mock_post.assert_called_once_with("/toggleOffline?offlineMessage=" + offline_message.replace(" ", "%20"))


def test_is_idle(patch_node_api):
    n = Node("http://localhost:8080/computer/agent1")

    assert n.is_idle is True


def test_wait_for_idle(monkeypatch):
    mock_get_api_data = MagicMock()

    def mock_get_api_data_fn():
        if not hasattr(mock_get_api_data_fn, "is_called"):
            mock_get_api_data_fn.is_called = True
            return {'idle': False}

        return {'idle': True}

    mock_get_api_data.side_effect = mock_get_api_data_fn
    monkeypatch.setattr(Node, "get_api_data", mock_get_api_data)

    n = Node("http://localhost:8080/computer/agent1")
    final_is_idle_value = n.wait_for_idle()

    assert final_is_idle_value is True
    assert mock_get_api_data.call_count >= 2


def test_wait_for_idle_timeout(monkeypatch):
    monkeypatch.setattr(Node, "get_api_data", lambda s: {'idle': False})

    n = Node("http://localhost:8080/computer/agent1")

    #TODO: Consider launching this method asynchronously somehow to prevent deadlocks if the wait method has bugs in it
    expected_idle_time_in_seconds = 2
    start_time = time.time()
    final_is_idle_value = n.wait_for_idle(expected_idle_time_in_seconds)
    duration_in_seconds = time.time() - start_time

    assert final_is_idle_value is False
    assert duration_in_seconds >= expected_idle_time_in_seconds

        
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
