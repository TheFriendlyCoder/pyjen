import unittest
import subprocess
import shlex
import datetime

class regression_tests(unittest.TestCase):
    def setUp(self):
        
        print "Setting Up"
         
    def tearDown(self):
        print "Tearing Down"
        
    def test1(self):
        print "In test one"
        
    def test2(self):
        print "In test two"
        
if __name__ == "__main__":
    #suite = unittest.TestLoader().loadTestsFromTestCase(regression_tests)
    #unittest.TextTestRunner(verbosity=3).run(suite)
    path_to_jenkins="C:/Users/kphillips/Documents/eclipse/pyjen/jenkins/jenkins.war"
    path_to_java="C:/Progra~1/Java/jre7/bin/java.exe"
    cmd_line = path_to_java + " -jar " + path_to_jenkins
    args = shlex.split(cmd_line)
    
    
    print str(datetime.datetime.now()) + ": Launching Jenkins..."
    #p = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = subprocess.Popen(args, stderr=subprocess.PIPE)
    print "launched"
    
    #Wait until the Jenkins service has completed its startup
    jenkinsRunning = False
    stdoutdata = None
    stderrdata = None
    while True:
        stderrdata = p.stderr.readline()
        print str(datetime.datetime.now()) + ": stderr " + stderrdata
        
        if stderrdata.find("Jenkins is fully up and running") >= 0:
            jenkinsRunning = True
            break
    
    if jenkinsRunning:
        print str(datetime.datetime.now()) + ":is running"
    else:
        print str(datetime.datetime.now()) + ":failed to launch"
    
    print stderrdata
    p.terminate()
        