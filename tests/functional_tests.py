import unittest
from test_utils import start_jenkins
from pyjen.jenkins import jenkins
from pyjen.view import view
import os
import shutil

class regression_tests(unittest.TestCase):
    
    #Reference to the subprocess object that manages the Jenkins
    #instance which runs concurrently with these tests
    __jenkins_process = None
    
    #URL of main dashboard for the local Jenkins instance
    __jenkins_url = "http://localhost:8080"
       
    @classmethod
    def setUpClass(self):
        print "Preparing Jenkins Instance..."
        self.__jenkins_home = os.path.abspath("./jenkins_home")
        #TODO: Detect whether jenkins is already running at the default URL and prompt user if we should just use that one
        self.__jenkins_process = start_jenkins(self.__jenkins_home)
         
    @classmethod
    def tearDownClass(self):
        #shut Jenkins down
        if self.__jenkins_process != None:
            self.__jenkins_process.terminate()
            
        #clean up working folder
        if os.path.exists(self.__jenkins_home):
            shutil.rmtree(self.__jenkins_home)
    
    def test_create_view(self):
        new_view_name = "test_view"
        j = jenkins(self.__jenkins_url)
        j.create_view(new_view_name, view.LIST_VIEW)
        v = j.find_view(new_view_name)
        
        self.assertTrue(v != None)
        
        self.assertEqual(self.__jenkins_url + "/view/" + new_view_name + "/", v.get_url())
        
    def test_shutdown(self):
        j = jenkins(self.__jenkins_url)

        self.assertFalse(j.is_shutting_down())
        j.prepare_shutdown()
        self.assertTrue(j.is_shutting_down())
        
        j.cancel_shutdown()
        self.assertFalse(j.is_shutting_down())

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(regression_tests)
    unittest.TextTestRunner(verbosity=3).run(suite)    