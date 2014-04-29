from pyjen.view import view
import unittest
from pyjen.user_params import GlobalParams

class mock_view_with_jobs_data_requester:
    def __init__ (self, url):
        pass
    
    def get_api_data(self):
        jobs = []
        r1 = {'url':'first/job'}
        r2 = {'url':'second/job'}
        jobs.append(r1)
        jobs.append(r2)
        
        retval = {}
        retval['jobs'] = jobs
        return retval
    

class view_tests(unittest.TestCase):

    def setUp(self):
        """Configures global connection parameters for use by test suite"""
        GlobalParams().set_jenkins_url("http://test_jenkins_url/")
        
    def test_get_all_jobs(self):
        v = view('', mock_view_with_jobs_data_requester)
        jobs = v.get_jobs()
        self.assertIsNotNone(jobs, "get_jobs method should return a list of jobs")
        self.assertEqual(2, len(jobs), "there should be 2 jobs returned by the get_jobs method")
        self.assertEqual('http://test_jenkins_url/first/job/', jobs[0].get_url(), "url of first job not set as expected")
        self.assertEqual('http://test_jenkins_url/second/job/', jobs[1].get_url(), "url of second job not set as expected")
    
    def test_get_url(self):
        expected_view_url = 'http://test_jenkins_url/view/myview/'
        v = view(expected_view_url)
        self.assertEqual(expected_view_url, v.get_url(), "View URL not being reported correctly")
        
    def test_delete_view(self):
#        mock_requester = post_validate_requester("/doDelete")
#        v = view('', custom_data_requester=mock_requester)
#        v.delete()
        pass
            
if __name__ == "__main__":
    unittest.main()