import unittest
from pyjen.node import Node
from mock import MagicMock
import pytest
import time

class node_misc_tests(unittest.TestCase):
    """Tests for remaining utility methods of the Node class not tested by other cases"""
    def test_get_name(self):
        expected_name = "node1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'displayName':expected_name}
        
        n = Node(mock_data_io)
        actual_name = n.name

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")
    def test_is_offline(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'offline':True}
        
        n = Node(mock_data_io)
        
        self.assertTrue(n.is_offline, "Node object should report the Node as being offline")
        
    def test_toggle_offline(self):
        mock_data_io = MagicMock()
        
        n = Node(mock_data_io)
        n.toggle_offline()
        
        mock_data_io.post.assert_called_once_with("/toggleOffline")
        
    def test_toggle_offline_with_message(self):
        mock_data_io = MagicMock()
        
        n = Node(mock_data_io)
        offline_message = "Description"
        n.toggle_offline(offline_message)
        
        mock_data_io.post.assert_called_once_with("/toggleOffline?offlineMessage=" + offline_message)

    def test_toggle_offline_with_message_with_spaces(self):
        mock_data_io = MagicMock()
        
        n = Node(mock_data_io)
        offline_message = "Descriptive text goes here"
        n.toggle_offline(offline_message)

        mock_data_io.post.assert_called_once_with("/toggleOffline?offlineMessage=Descriptive%20text%20goes%20here")    
        
    def test_is_idle(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'idle':True}
        
        n = Node(mock_data_io)
        
        self.assertTrue(n.is_idle, "Node should have an idle state.")
        
    def test_wait_for_idle(self):
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
        
    def test_wait_for_idle_timeout(self):
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
