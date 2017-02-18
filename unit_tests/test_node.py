from pyjen.node import Node
import pytest
import time


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


@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
def test_toggle_offline():
    mock_data_io = MagicMock()

    n = Node(mock_data_io)
    n.toggle_offline()

    mock_data_io.post.assert_called_once_with("/toggleOffline")


@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
def test_toggle_offline_with_message():
    mock_data_io = MagicMock()

    n = Node(mock_data_io)
    offline_message = "Description"
    n.toggle_offline(offline_message)

    mock_data_io.post.assert_called_once_with("/toggleOffline?offlineMessage=" + offline_message)


@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
def test_toggle_offline_with_message_with_spaces():
    mock_data_io = MagicMock()

    n = Node(mock_data_io)
    offline_message = "Descriptive text goes here"
    n.toggle_offline(offline_message)

    mock_data_io.post.assert_called_once_with("/toggleOffline?offlineMessage=Descriptive%20text%20goes%20here")


def test_is_idle(patch_node_api):
    n = Node("http://localhost:8080/computer/agent1")

    assert n.is_idle is True


@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
def test_wait_for_idle():
    mock_data_io = MagicMock()

    def mock_get_api_data():
        if not hasattr(mock_get_api_data, "is_called"):
            mock_get_api_data.is_called = True
            return {'idle':False}

        return {'idle':True}

    mock_data_io.get_api_data.side_effect = mock_get_api_data

    n = Node(mock_data_io)
    final_is_idle_value = n.wait_for_idle()

    self.assertTrue(final_is_idle_value)
    self.assertGreaterEqual(mock_data_io.get_api_data.call_count, 2, "Mock dataio object should have been called at least twice.")


@pytest.mark.skip(reason="To be refactored to use pytest fixtures")
def test_wait_for_idle_timeout():
    mock_data_io = MagicMock()
    mock_data_io.get_api_data.return_value = {'idle':False}

    n = Node(mock_data_io)

    #TODO: Consider launching this method asynchronously
    #somehow to prevent deadlocks if the wait method has bugs in it
    start_time = time.time()
    final_is_idle_value = n.wait_for_idle(3.1)
    duration_in_seconds = time.time() - start_time

    self.assertGreaterEqual(duration_in_seconds, 3, "wait method should have taken at least 3 seconds to complete")
    self.assertFalse(final_is_idle_value)
        
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
