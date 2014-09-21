import unittest
import pytest
from test_utils import start_jenkins, get_jenkins_wars, safe_shutdown, safe_delete
from pyjen.jenkins import Jenkins
from pyjen.view import View
import os
import shutil
import stat


    
class empty_jenkins_regression_tests(unittest.TestCase):
    """Tests that require a clean, unfettered Jenkins instance"""
    
    @classmethod
    def setUpClass(self):
        
        print ("Preparing Jenkins Instance...")
        path = os.path.join(os.getcwd(), "jenkins")
        get_jenkins_wars(path)
        
        test_dir = os.path.dirname(os.path.realpath(__file__))

        self._jenkins_home = os.path.abspath(os.path.join(test_dir, "empty_jenkins_home"))
        if not os.path.exists(self._jenkins_home):
            os.makedirs(self._jenkins_home)
        
        self._jenkins_process = start_jenkins(os.path.join(path, "jenkins_lts.war"), self._jenkins_home)
        
        self._jenkins_url = "http://localhost:8080"
         
    @classmethod
    def tearDownClass(self):
        if self._jenkins_process != None:
            self._jenkins_process.terminate()
            self._jenkins_process.wait()
            
        #clean up working folder
        safe_delete(self._jenkins_home)
    
    def test_create_view(self):
        new_view_name = "test_create_view"
        j = Jenkins.easy_connect(self._jenkins_url, None)
        j.create_view(new_view_name, View.LIST_VIEW)
        v = j.find_view(new_view_name)
        
        self.assertTrue(v != None)
        
        self.assertEqual(v.name, new_view_name)
        
    def test_shutdown(self):
        j = Jenkins.easy_connect(self._jenkins_url, None)

        self.assertFalse(j.is_shutting_down)
        j.prepare_shutdown()
        self.assertTrue(j.is_shutting_down)
        
        j.cancel_shutdown()
        self.assertFalse(j.is_shutting_down)

    def test_default_view(self):
        j = Jenkins.easy_connect(self._jenkins_url, None)
        
        v = j.default_view
        self.assertTrue(v != None)
        self.assertEqual("All", v.name)
        
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
