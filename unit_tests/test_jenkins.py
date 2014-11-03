import unittest
from pyjen.jenkins import Jenkins
from pyjen.exceptions import InvalidParameterError
from mock import MagicMock
import pytest

class jenkins_misc_tests(unittest.TestCase):
    """Tests for remaining utility methods of the Jenkins class not tested by other cases"""
    def test_get_version(self):
        expected_version = "1.2.3"
        
        mock_data_io = MagicMock()
        mock_data_io.get_headers.return_value = {'x-jenkins':expected_version}
        
        j = Jenkins(mock_data_io)

        self.assertEqual(expected_version, j.version)
        self.assertEqual("call('/api/python')", str(mock_data_io.get_headers.call_args), 
                         "get_version method should have attempted to load HTTP header info from the api/python URL")
        self.assertEqual(mock_data_io.get_headers.call_count, 1, 
                                "get_headers method should have been called one time")
        
    def test_get_unknown_version(self):
        expected_version = "Unknown"
        
        mock_data_io = MagicMock()
        mock_data_io.get_headers.return_value = {}
        
        j = Jenkins(mock_data_io)

        self.assertEqual(expected_version, j.version)
        self.assertEqual("call('/api/python')", str(mock_data_io.get_headers.call_args), 
                         "get_version method should have attempted to load HTTP header info from the api/python URL")
        self.assertEqual(mock_data_io.get_headers.call_count, 1, 
                                "get_headers method should have been called one time")
        
    def test_prepare_shutdown(self):
        mock_data_io = MagicMock()
        
        j = Jenkins(mock_data_io)
        j.prepare_shutdown()
        
        self.assertEqual("call('/quietDown')", str(mock_data_io.post.call_args))
        self.assertEqual(mock_data_io.post.call_count, 1, "post method should have only been called once")
    
    def test_cancel_shutdown(self):
        mock_data_io = MagicMock()
        
        j = Jenkins(mock_data_io)
        j.cancel_shutdown()
        
        self.assertEqual("call('/cancelQuietDown')", str(mock_data_io.post.call_args))
        self.assertEqual(mock_data_io.post.call_count, 1, "post method should have only been called once")
    
    def test_is_shutting_down(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {"quietingDown":True}
        
        j = Jenkins(mock_data_io)
        self.assertTrue(j.is_shutting_down, "Object should be preparing for shutdown")

    def test_job_types(self):
        mock_data_io = MagicMock()
        j = Jenkins(mock_data_io)
        actual = j.job_types
        self.assertIn("freestyle", actual)
        
class jenkins_job_tests(unittest.TestCase):
    def setUp(self):
        """Configure a mock dataio object which supports a few mock job objects"""
        self.job1_name = 'MyFirstJob'
        self.job1_url = 'http://localhost:8080/job/MyFirstJob'
        self.job2_name = 'SecondJob'
        self.job2_url = 'http://localhost:8080/job/SecondJob'
            
        # io objects used by the two views managed by our mock Jenkins instance
        self.job1_mock_data_io = MagicMock()
        self.job1_mock_data_io.get_api_data.return_value = {'name':self.job1_name}
        self.job1_mock_data_io.get_text.return_value = "<project></project>"
        self.job2_mock_data_io = MagicMock()
        self.job2_mock_data_io.get_api_data.return_value = {'name':self.job2_name}
        self.job2_mock_data_io.get_text.return_value = "<project></project>"
        
        # mock jenkins instance which exposes 2 views
        self.mock_jenkins_data_io = MagicMock()
        mock_jobs = []
        mock_jobs.append({'url':self.job1_url,'name':self.job1_name})
        mock_jobs.append({'url':self.job2_url,'name':self.job2_name})
        self.mock_jenkins_data_io.get_api_data.return_value = {'jobs':mock_jobs}
        self.mock_jenkins_data_io.clone.side_effect = self.mock_clone
        self.mock_jenkins_data_io.url.return_value = "http://localhost:8080"
        
        
    def mock_clone(self, url):
        """Function used to mock the clone() method of the mock_jenkins_data_io object"""
        if url == self.job1_url:
            return self.job1_mock_data_io
        if url == self.job2_url:
            return self.job2_mock_data_io
                
        self.fail("Unexpected URL parameter to dataio clone method: " + url)

    def test_find_job_no_jobs(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'jobs':{}}
        
        j = Jenkins(mock_data_io)
        njob = j.find_job("MyJob")
        self.assertEqual(njob, None, "No jobs should be found by the search method")
        
    def test_find_job_success(self):
        j = Jenkins(self.mock_jenkins_data_io)
        job = j.find_job(self.job2_name)
        
        self.assertNotEqual(job, None, "find_job should have returned a valid job object")
        self.mock_jenkins_data_io.clone.assert_called_with(self.job2_url)

    def test_create_job(self):
        expected_name = "TestJob"
        jenkins_data_io = MagicMock()

        job_data_io = MagicMock()
        job_data_io.get_text.return_value = "<project></project>"
        job_data_io.get_api_data.return_value = {"name": expected_name}
        jenkins_data_io.clone.return_value = job_data_io

        j = Jenkins(jenkins_data_io)
        job = j.create_job(expected_name, "freestyle")

        self.assertEqual(job.name, expected_name)

class jenkins_view_tests(unittest.TestCase):
    """Unit tests for the view-related methods of the Jenkins class"""
    
    def setUp(self):
        """Configure a mock dataio object which supports a few mock view objects"""
        self.primary_view_name = 'main'
        jenkins_root_url = 'http://localhost:8080/'
        self.primary_view_url = jenkins_root_url + "view/" + self.primary_view_name
        self.view2_name = 'secondView'
        self.view2_url = 'http://localhost:8080/view/secondView'
        
        self.view2_job1_url = 'http://localhost:8080/job/j1'
        self.view2_job1_name = 'j1'
        mock_job1_dataio = MagicMock()
        mock_job1_dataio.get_api_data.return_value = {"name":self.view2_job1_name}
        mock_job1_dataio.get_text.return_value = "<project></project>"

        # io objects used by the two views managed by our mock Jenkins instance
        self.mock_primary_view_data_io = MagicMock()
        self.mock_primary_view_data_io.get_api_data.return_value = {'name':self.primary_view_name}
        # TODO: double check to make sure this is the corrrect view type
        self.mock_primary_view_data_io.get_text.return_value = "<hudson.model.ListView/>"
        self.mock_view2_data_io = MagicMock()
        self.mock_view2_data_io.get_api_data.return_value = {'name':self.view2_name, 'jobs':[{'url':self.view2_job1_url}]}
        self.mock_view2_data_io.clone.side_effect = self.mock_clone
        self.mock_view2_data_io.get_text.return_value = "<hudson.model.ListView/>"

        # mock jenkins instance which exposes 2 views
        self.mock_jenkins_data_io = MagicMock()
        mock_views = []
        mock_views.append({'url':self.view2_url,'name':self.view2_name})
        mock_views.append({'url':jenkins_root_url,'name':self.primary_view_name})
        self.mock_jenkins_data_io.get_api_data.return_value = {'views':mock_views,'primaryView':mock_views[1]}
        self.mock_jenkins_data_io.url = jenkins_root_url
        
        # construct mock 'clone' method such that views created by
        # these unit tests will behave correctly
        self.mock_jenkins_data_io.clone.side_effect = self.mock_clone
        self.clone_map = {}
        self.clone_map[self.primary_view_url] = self.mock_primary_view_data_io
        self.clone_map[self.view2_url] = self.mock_view2_data_io
        self.clone_map[self.view2_job1_url] = mock_job1_dataio

        
    def mock_clone(self, url):
        """Function used to mock the clone() method of the mock_jenkins_data_io object"""
        if not url in self.clone_map:
            self.fail("Unexpected URL parameter to dataio clone method: " + url)
        return self.clone_map[url]

    
    def test_get_default_view(self):        
        # test logic
        j = Jenkins(self.mock_jenkins_data_io)
        v = j.default_view
        actual_view_name = v.name
        
        # verification
        self.assertEqual(actual_view_name, self.primary_view_name)
        self.mock_jenkins_data_io.clone.assert_called_with(self.primary_view_url)
    
    def test_get_multiple_views(self):
        # test logic
        j = Jenkins(self.mock_jenkins_data_io)
        views = j.all_views
        
        # verification
        self.assertEqual(len(views), 2)
        self.assertEqual(views[0].name, self.view2_name)
        self.assertEqual(views[1].name, self.primary_view_name)
    
    def test_find_view(self):
        # test logic
        j = Jenkins(self.mock_jenkins_data_io)
        View = j.find_view(self.view2_name)
        
        # verification
        self.assertNotEqual(View, None, "code should return a valid pyjen.view object")
        self.assertEqual(View.name, self.view2_name, "incorrect view returned by jenkins object")
        self.mock_jenkins_data_io.clone.assert_called_once_with(self.view2_url)
        
    def test_find_view_primary_view(self):        
        # test logic
        j = Jenkins(self.mock_jenkins_data_io)
        View = j.find_view(self.primary_view_name)
        
        # verification
        self.assertNotEqual(View, None, "code should return a valid pyjen.view object")
        self.assertEqual(View.name, self.primary_view_name, "incorrect view returned by jenkins object")
        self.mock_jenkins_data_io.clone.assert_called_once_with(self.primary_view_url)
    
    def test_find_missing_view(self):
        # test logic
        j = Jenkins(self.mock_jenkins_data_io)
        View = j.find_view("DoesNotExist")
    
        # verification
        self.assertEqual(View, None, "No valid view should have been found.")
        
    def test_create_view(self):
        new_view_url = "http://localhost:8080/view/MyView"
        new_view_name = "MyView"
        new_view_dataio = MagicMock()
        new_view_dataio.get_api_data.return_value = {'name':new_view_name}
        new_view_dataio.get_text.return_value = "<hudson.model.ListView/>"
        self.mock_jenkins_data_io.get_api_data.return_value['views'].append({'url':new_view_url,'name':new_view_name})
        self.clone_map[new_view_url] = new_view_dataio
        j = Jenkins(self.mock_jenkins_data_io)
        v = j.create_view(new_view_name, "ListView")
        
        self.assertEqual(v.name, new_view_name)

class jenkins_nodes_tests(unittest.TestCase):
    """Unit tests for the node-related methods of the Jenkins class"""
    
    def setUp(self):
        """Configure a mock dataio object which supports a few mock node objects"""
        jenkins_root_url = 'http://localhost:8080'
        self.root_computer_url = jenkins_root_url + "/computer"
        self.master_node_name = "master"
        self.master_node_url = self.root_computer_url + "/(master)"
        self.second_node_name = "OtherNode"
        self.second_node_url = self.root_computer_url + "/OtherNode"
        
        # io objects used by the two nodes managed by our mock Jenkins instance
        self.mock_root_node_data_io = MagicMock()
        mock_nodes = []
        mock_nodes.append({"displayName":self.master_node_name})
        mock_nodes.append({"displayName":self.second_node_name})
        self.mock_root_node_data_io.get_api_data.return_value = {"computer":mock_nodes}
        
        self.mock_master_node_data_io = MagicMock()
        self.mock_master_node_data_io.get_api_data.return_value = {'displayName':self.master_node_name}
        self.mock_second_node_data_io = MagicMock()
        self.mock_second_node_data_io.get_api_data.return_value = {'displayName':self.second_node_name}
        
        # mock jenkins instance which exposes 2 nodes
        self.mock_jenkins_data_io = MagicMock()
        self.mock_jenkins_data_io.url = jenkins_root_url        
        self.mock_jenkins_data_io.clone.side_effect = self.mock_clone
        
        
    def mock_clone(self, url):
        """Function used to mock the clone() method of the mock_jenkins_data_io object"""
        
        if url == self.master_node_url:
            return self.mock_master_node_data_io
        if url == self.second_node_url:
            return self.mock_second_node_data_io
        if url == self.root_computer_url:
            return self.mock_root_node_data_io
        
        self.fail("Unexpected URL parameter to dataio clone method: " + url)
    
    def test_get_multiple_nodes(self):
        j = Jenkins(self.mock_jenkins_data_io)
        nodes = j.nodes
        
        self.assertNotEqual(nodes, None)
        self.assertEqual(2, len(nodes), "Mock jenkins instance should expose 2 connected nodes.")
        self.assertEqual(self.master_node_name, nodes[0].name)
        self.assertEqual(self.second_node_name, nodes[1].name)
    
if __name__ == "__main__":
    pytest.main()
    