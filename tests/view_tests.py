from pyjen.view import view
import unittest
import test_utils

class mock_view_with_jobs_data_requester:
    __user = ""
    __pass = ""
    def __init__ (self, user=None, password=None):
        self.__user = user
        self.__pass = password
    
    def get_data(self, sub_url=None):
        jobs = []
        r1 = {'url':'first/job'}
        r2 = {'url':'second/job'}
        jobs.append(r1)
        jobs.append(r2)
        
        retval = {}
        retval['jobs'] = jobs
        return retval
    def get_user(self):
        return self.__user
    def get_password(self):
        return self.__pass

class view_tests(unittest.TestCase):
    def test_get_all_jobs(self):
        mock_requester = mock_view_with_jobs_data_requester()
        v = view('', custom_data_requester=mock_requester)
        jobs = v.get_jobs()
        self.assertIsNotNone(jobs, "get_jobs method should return a list of jobs")
        self.assertEqual(2, len(jobs), "there should be 2 jobs returned by the get_jobs method")
        self.assertEqual('first/job', jobs[0].get_url(), "url of first job not set as expected")
        self.assertEqual('second/job', jobs[1].get_url(), "url of second job not set as expected")
    
    def test_get_all_jobs_with_authentication(self):
        mock_requester = mock_view_with_jobs_data_requester('MyUser', 'MyPass')
        v = view('', custom_data_requester=mock_requester)
        jobs = v.get_jobs()
        
        for j in jobs:
            self.assertEqual('MyUser', j.get_authenticated_user(), "Username of job object not inherited from the view")
            self.assertEqual('MyPass', j.get_authenticated_password(), "Password of job object not inherited from the view")

if __name__ == "__main__":
    unittest.main()