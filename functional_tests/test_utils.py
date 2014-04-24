import subprocess
import shlex
import os
import locale

def start_jenkins(home_folder=None):
    """Attempts to launch an isolated instance of Jenkins for testing purposes
    
    This function will block until the instance of Jenkins is successfully
    loaded and ready for use by subsequent test logic
    
    NOTE: The host OS must have the JAVA_HOME environment variable set and it
    must point to a supported version of java under which Jenkins will be run. 
    
    Returns
    -------
    subprocess
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
        
    path_to_jenkins="../jenkins/jenkins.war"
    
    java_options=""
    if home_folder:
        java_options=' -DJENKINS_HOME="' + home_folder + '"'

    cmd_line = '"' + java_app + '"' + java_options + ' -jar ' + path_to_jenkins
    args = shlex.split(cmd_line)
    
    #Now launch Jenkins in a secondary, non-blocking process
    jenkins_process = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    #Wait until the Jenkins service has completed its startup before continuing
    jenkinsRunning = False
    
    encoding = locale.getdefaultlocale()[1]
    while True:
        #TODO: probably should stream this output to a log file somewhere for debugging
        stderrdata = jenkins_process.stderr.readline()
        tmp = stderrdata.decode(encoding)
        if tmp.find("Jenkins is fully up and running") >= 0:
            jenkinsRunning = True
            break

    if not jenkinsRunning:
        raise "Failed to launch Jenkins instance: " + path_to_jenkins
    
    return jenkins_process

if __name__ == "__main__":
    pass