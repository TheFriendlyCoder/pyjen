import pytest
from functional_tests.test_utils import start_jenkins, get_jenkins_war, safe_delete
from pyjen.jenkins import Jenkins
from pyjen.view import View
import os
from testtools import TestCase
import tempfile

class lts_tests(TestCase):
    @classmethod
    def setUpClass(self):
        #todo - setup temp folder for home older
        #print ("Preparing Jenkins Instance...")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jenkins")
        war_file = get_jenkins_war(path, "lts")
        
        self._jenkins_home = tempfile.mkdtemp(prefix="pyjen_test")
        
        self._jenkins_process = start_jenkins(war_file, self._jenkins_home)
        
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


class latest_tests(lts_tests):
    @classmethod
    def setUpClass(self):
        #todo - setup temp folder for home older
        #print ("Preparing Jenkins Instance...")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jenkins")
        war_file = get_jenkins_war(path, "latest")
        
        self._jenkins_home = tempfile.mkdtemp(prefix="pyjen_test")
        
        self._jenkins_process = start_jenkins(war_file, self._jenkins_home)
        
        self._jenkins_url = "http://localhost:8080"
         
    @classmethod
    def tearDownClass(self):
        if self._jenkins_process != None:
            self._jenkins_process.terminate()
            self._jenkins_process.wait()
            
        #clean up working folder
        safe_delete(self._jenkins_home)
        
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
    