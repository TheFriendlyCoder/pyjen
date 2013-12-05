import unittest
import subprocess
import shlex
import datetime

class regression_tests(unittest.TestCase):
    __path_to_jenkins="../jenkins/jenkins.war"
    __jenkins_process = None
    def setUp(self):
        
        cmd_line = "java -jar " + self.__path_to_jenkins
        args = shlex.split(cmd_line)
        self.__jenkins_process = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        #Wait until the Jenkins service has completed its startup
        jenkinsRunning = False
        while True:
            #TODO: probably should stream this output to a log file somewhere for debugging
            stderrdata = self.__jenkins_process.stderr.readline()
            if stderrdata.find("Jenkins is fully up and running") >= 0:
                jenkinsRunning = True
                break
    
        self.assertTrue(jenkinsRunning, "Failed to launch jenkins instance")
         
    def tearDown(self):
        self.__jenkins_process.terminate()
        
    def test1(self):
        print "In test one"

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(regression_tests)
    unittest.TextTestRunner(verbosity=3).run(suite)
    
    
    print stderrdata
    p.terminate()
        