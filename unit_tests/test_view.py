from pyjen.view import view
import unittest
from pyjen.user_params import GlobalParams
import mock_data_requester

class view_tests(unittest.TestCase):

    def setUp(self):
        """Configures global connection parameters for use by test suite"""
        GlobalParams().set_jenkins_url("http://test_jenkins_url/")
        
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
            
if __name__ == "__main__":
    unittest.main()