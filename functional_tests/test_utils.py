"""Helper functions used by the pyjen functional tests"""
import subprocess
import shlex
import os
import locale
import urllib.request as urllib
import math
import sys
import stat
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

    args = []
    
    #Generate a command line for running Jenkins in an isolated environment
    if java_home:
        java_app = os.path.join(java_home, "bin", "java")
    else:
        #if JAVA_HOME env var is undefined lets assume the java executable
        #can be located on the global system path
        java_app = "java"
    
    args.append(java_app)
    args.append('-DJENKINS_HOME=' + home_folder)
    args.append("-jar")
    args.append(war_file)

    print ("Starting Jenkins on port 8080...")
    #Now launch Jenkins in a secondary, non-blocking process
    jenkins_process = subprocess.Popen( args , stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    #Wait until the Jenkins service has completed its startup before continuing
    jenkins_running = False
    
    while True:
        stderrdata = jenkins_process.stdout.readline()
        tmp = stderrdata
        if tmp.find("Jenkins is fully up and running") >= 0:
            jenkins_running = True
            break
        if tmp.find("Error") >= 0:
            break

    if not jenkins_running:
        raise RuntimeError("Failed to launch Jenkins instance: " + war_file + "\n" + tmp)
    
    print ("done startup")
    return jenkins_process


    
def safe_delete (path):
    if not os.path.exists(path):
        return
    
    for root, dirs, files in os.walk(path):
        for fname in files:
            full_path = os.path.join(root, fname)
            os.chmod(full_path ,stat.S_IWRITE)
    
    shutil.rmtree(path)
    
def get_jenkins_wars (output_path):
    """Downloads the latest and LTS versions of the Jenkins WAR file
    
    if any .war files already exist in the target folder they will not
    be overwitten
    
    :param str output_path: path to the folder to download the war files to
    """
    lts_url = "http://mirrors.jenkins-ci.org/war-stable/latest/jenkins.war"
    lts_output_file = os.path.join(output_path, "jenkins_lts.war")
    latest_url = "http://mirrors.jenkins-ci.org/war/latest/jenkins.war"
    latest_output_file = os.path.join(output_path, "jenkins_latest.war")
    
    if os.path.exists(lts_output_file):
        print ("Jenkins LTS file already exists. Skipping download.")
    else:
        print ("Downloading Jenkins LTS: ", end="")
        urllib.urlretrieve(lts_url, lts_output_file, _progress_hook)
        print ("")
        
    if os.path.exists(latest_output_file):
        print ("Jenkins latest file already exists. Skipping download.")
    else:
        print ("Downloading Jenkins latest: ", end="")
        urllib.urlretrieve(latest_url, latest_output_file, _progress_hook)
        print("")
    
def _progress_hook(block_number, block_size, total_size):
    """Callback used by `func`:get_jenkins_wars to report the download progress
    :param int block_number: the current data block being downloaded
    :param int block_size: the size, in bytes, of each downloaded block
    :param int total_size: the total number of bytes being downloaded
    """
    if block_number == 0:
        _progress_hook.counter = 0
        print ("10..", end="")
        sys.stdout.flush()
    total_blocks = math.ceil(total_size / block_size)
    
    percent_done = math.ceil(block_number / total_blocks * 100)
    
    increment = math.floor(percent_done / 10)
    if increment != _progress_hook.counter:
        msg = str(10-increment)
        if increment != 10:
            msg += ".."
        print (msg, end="")
        sys.stdout.flush()
    _progress_hook.counter = increment

import shutil
if __name__ == "__main__":
    #path = os.path.join(os.getcwd())
    #get_jenkins_wars(path)
    
    home = os.path.join(os.getcwd(), "empty home")
    #if os.path.exists(home):
    #    shutil.rmtree(home)
    #os.makedirs(home)
    print ("starting jenkins")
    p = start_jenkins("jenkins_lts.war", home)
    p.terminate()
    print ("Done")
    #safe_shutdown(p)
    