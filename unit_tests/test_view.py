from pyjen.view import view
import unittest
from mock import MagicMock

class view_tests(unittest.TestCase):
    
    def test_get_name(self):
        expected_name = "MyView1"
        
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':expected_name}
        
        v = view(mock_data_io)
        actual_name = v.get_name()

        self.assertEqual(expected_name, actual_name)
        self.assertEqual(mock_data_io.get_api_data.call_count, 1, 
                                "get_api_data method should have been called one time")
    def test_job_count(self):
        mock_data_io = MagicMock()
        mock_data_io.get_api_data.return_value = {'name':"MyView1", 'jobs':[{'url':'foo'},{'url':'bar'}]}
        
        v = view(mock_data_io)
        expected_count = v.job_count()

        self.assertEqual(expected_count, 2, "There should be 2 jobs in the mock view")
        
    """    
    def test_get_jobs(self):
        data = {}
        data['jobs'] = [{'url':'first/job'}, {'url':'second/job'} ]
        v = view(data, mock_data_requester.dictionary_based_requester)
        
        jobs = v.get_jobs()
        
        self.assertIsNotNone(jobs, "get_jobs method should return a list of jobs")
        self.assertEqual(2, len(jobs), "there should be 2 jobs returned by the get_jobs method")
        self.assertEqual('http://test_jenkins_url/first/job/', jobs[0].get_url(), "url of first job not set as expected")
        self.assertEqual('http://test_jenkins_url/second/job/', jobs[1].get_url(), "url of second job not set as expected")
    
    def test_get_jobs_empty(self):
        data = {}
        data['jobs'] = []
        v = view(data, mock_data_requester.dictionary_based_requester)
        
        jobs = v.get_jobs()
        self.assertEqual(0, len(jobs), "List of jobs exposed by view should be empty")
        
    def test_get_url(self):
        expected_view_url = 'http://test_jenkins_url/view/myview/'
        
        v = view(expected_view_url)
        
        self.assertEqual(expected_view_url, v.get_url(), "View URL not being reported correctly")
    
    def test_get_name(self):
        data = {}
        data['name'] = 'Mock View Name'
        
        v = view(data, mock_data_requester.dictionary_based_requester)
        
        self.assertEqual(data['name'], v.get_name())
        
    def test_delete_view(self):
#        mock_requester = post_validate_requester("/doDelete")
#        v = view('', custom_data_requester=mock_requester)
#        v.delete()
        pass
            """
if __name__ == "__main__":
    unittest.main()