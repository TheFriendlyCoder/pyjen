import unittest
from test_utils import start_jenkins
from pyjen.jenkins import jenkins
from pyjen.view import view

class regression_tests(unittest.TestCase):
    
    #Reference to the subprocess object that manages the Jenkins
    #instance which runs concurrently with these tests
    __jenkins_process = None
    
    #URL of main dashboard for the local Jenkins instance
    __jenkins_url = "http://localhost:8080"
    
    def setUp(self):
        #TODO: Set the home folder for jenkins as part of this setup
        #TODO: Detect whether jenkins is already running at the default URL and prompt user if we should just use that one
        self.__jenkins_process = start_jenkins()
        pass
         
    def tearDown(self):
        #TODO: After Jenkins is terminated we need to delete any cached home folders or do a Git clean
        if self.__jenkins_process != None:
            self.__jenkins_process.terminate()
        
    
    def test_create_view(self):
        new_view_name = "test_view"
        j = jenkins(self.__jenkins_url)
        j.create_view(new_view_name, view.LIST_VIEW)
        v = j.find_view(new_view_name)
        
        self.assertTrue(v != None)
        
        self.assertEqual(self.__jenkins_url + "/view/" + new_view_name + "/", v.get_url())
        
        

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(regression_tests)
    unittest.TextTestRunner(verbosity=3).run(suite)   
    #j = jenkins('http://localhost:8080')
    #j.create_view('asdf', view.LIST_VIEW)
    