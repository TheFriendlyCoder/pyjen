"""Helper functions used by the pyjen functional tests"""
import subprocess
import shlex
import os
import locale

def start_jenkins(war_file, home_folder):
    """Attempts to launch an isolated instance of Jenkins for testing purposes
    
    This function will block until the instance of Jenkins is successfully
    loaded and ready for use by subsequent test logic
    
    :param str war_file: path to the Jenkins war file to be launched
    :param str home_folder: path to the folder to be used as the Jenkins home folder
    :returns:
        reference to the subprocess object used to launch Jenkins in a parallel
        process so as to not block the subsequent test execution.
        
        when this instance of Jenkins is no longer needed simply call the
        terminate() method on the returned object to close the app.
    """ 
    #see if we have a JAVA_HOME env var set
    java_home = os.getenv('JAVA_HOME')

    #Generate a command line for running Jenkins in an isolated environment
    if java_home:
        java_app = os.path.join(java_home, "bin", "java")
    else:
        #if JAVA_HOME env var is undefined lets assume the java executable
        #can be located on the global system path
        java_app = "java"
        
    java_options=' -DJENKINS_HOME="' + home_folder + '"'

    cmd_line = '"' + java_app + '"' + java_options + ' -jar ' + war_file
    args = shlex.split(cmd_line)

    #Now launch Jenkins in a secondary, non-blocking process
    jenkins_process = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    #Wait until the Jenkins service has completed its startup before continuing
    jenkins_running = False
    
    encoding = locale.getdefaultlocale()[1]
    while True:
        stderrdata = jenkins_process.stderr.readline()
        tmp = stderrdata.decode(encoding)
        if tmp.find("Jenkins is fully up and running") >= 0:
            jenkins_running = True
            break

    if not jenkins_running:
        raise "Failed to launch Jenkins instance: " + war_file
    
    return jenkins_process

if __name__ == "__main__":
    pass
