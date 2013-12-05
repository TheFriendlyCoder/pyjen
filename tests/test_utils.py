import subprocess
import shlex
from os import path, environ

def get_sample_data_file(filename):
    """Given a filename, this method generates the full path to the file in the sample data folder

    This method assumes that sample data is source data that
    typically represents data found in the real world under
    typical use of Jenkins. These files should never be modified
    during unit test execution.
    
    This method does basic validation to ensure the specified
    sample data file does exist. If it does not an appropriate
    unit test exception will be thrown.
    
    Parameters
    ----------
    filename : string
        name of the file to be located
    
    Returns
    -------
    string
        Full path and file name of the sample data to be loaded
    """
    
    working_path = path.dirname(path.realpath(__file__))
    retval =  working_path + "/sample_data/" + filename
    
    assert(path.exists(retval))
    
    return retval

def get_test_data_file(filename):
    """Given a filename, this method generates the full path to the file in the test data folder
    
    Test data is considered miscellaneous unit test data, such
    as those used to validate the output of a process under test.
    
    This method does basic validation to ensure the specified
    test data file does exist. If it does not an appropriate
    unit test exception will be thrown.
    
    Parameters
    ----------
    filename : string
        name of the file to be located
    
    Returns
    -------
    string
        Full path and file name of the test data to be loaded
    """
    
    working_path = path.dirname(path.realpath(__file__))
    retval =  working_path + "/test_data/" + filename
    
    assert(path.exists(retval))
    
    return retval

def start_jenkins():
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
    #Get the java installation folder from the environment
    if not 'JAVA_HOME' in environ:
        raise "JAVA_HOME environment variable not found"
    java_home = environ['JAVA_HOME']
    
    #Generate a command line for running Jenkins in an isolated environment
    path_to_jenkins="../jenkins/jenkins.war"
    cmd_line = '"' + java_home + '/java.exe" -jar ' + path_to_jenkins
    args = shlex.split(cmd_line)
    
    #Now launch Jenkins in a secondary, non-blocking process
    jenkins_process = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    #Wait until the Jenkins service has completed its startup before continuing
    jenkinsRunning = False
    while True:
        #TODO: probably should stream this output to a log file somewhere for debugging
        stderrdata = jenkins_process.stderr.readline()
        if stderrdata.find("Jenkins is fully up and running") >= 0:
            jenkinsRunning = True
            break

    if not jenkinsRunning:
        raise "Failed to launch Jenkins instance: " + path_to_jenkins
    
    return jenkins_process