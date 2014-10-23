"""Helper functions used by the pyjen functional tests"""
import subprocess
import shutil
import os

import math
import sys
import stat
import time

import random

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.request as urllib
    
lts_url = "http://mirrors.jenkins-ci.org/war-stable/latest/jenkins.war"
latest_url = "http://mirrors.jenkins-ci.org/war/latest/jenkins.war"

def start_jenkins(war_file, home_folder):
    """Attempts to launch an isolated instance of Jenkins for testing purposes
    
    This function will block until the instance of Jenkins is successfully
    loaded and ready for use by subsequent test logic
    
    :param str war_file: path to the Jenkins war file to be launched
    :param str home_folder: path to the folder to be used as the Jenkins home folder
    :return: 2-tuple reference to the subprocess object used to launch Jenkins and the URL of the test dashboard
        
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
    JENKINS_PORT=random.randrange(1000,1100)
    args.append("--httpPort={0}".format(JENKINS_PORT))

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
    
    # Give the Jenkins process a couple of seconds to finish startup just to be safe
    time.sleep(10)
    return (jenkins_process, "http://localhost:{0}".format(JENKINS_PORT))


    
def safe_delete (path):
    """Recursively deletes the contents of a given folder, even when files are read only
    
    :param str path: root folder to be deleted
    """
    if not os.path.exists(path):
        return
    
    for root, dirs, files in os.walk(path):
        for fname in files:
            full_path = os.path.join(root, fname)
            os.chmod(full_path ,stat.S_IWRITE)
    
    shutil.rmtree(path)
    
def get_jenkins_war (output_path, edition):
    """Downloads the latest and LTS versions of the Jenkins WAR file
    
    if any .war files already exist in the target folder they will not
    be overwitten
    
    :param str output_path: path to the folder to download the war files to
    :param str edition: specifies which version of Jenkins to find. Valid values are 'lts' and 'latest'
    :return: path to the downloaded war file
    :rtype: `func`:str
    """
    
    assert edition == "lts" or edition == "latest"
    if edition == "lts":
        src_url = lts_url
        output_file = os.path.join(output_path, "jenkins_lts.war")
    else:
        src_url = latest_url
        output_file = os.path.join(output_path, "jenkins_latest.war")
    
    if not os.path.exists(output_file):
        urllib.urlretrieve(src_url, output_file, _progress_hook)
        
    return output_file
    
def _progress_hook(block_number, block_size, total_size):
    """Callback used by `func`:get_jenkins_wars to report the download progress
    :param int block_number: the current data block being downloaded
    :param int block_size: the size, in bytes, of each downloaded block
    :param int total_size: the total number of bytes being downloaded
    """
    if block_number == 0:
        _progress_hook.counter = 0
        #print ("10..", end="")
        sys.stdout.flush()
    total_blocks = math.ceil(total_size / block_size)
    
    percent_done = math.ceil(block_number / total_blocks * 100)
    
    increment = math.floor(percent_done / 10)
    if increment != _progress_hook.counter:
        msg = str(10-increment)
        if increment != 10:
            msg += ".."
        #print (msg, end="")
        sys.stdout.flush()
    _progress_hook.counter = increment

if __name__ == "__main__":
    #path = os.path.join(os.getcwd())
    #war_file = get_jenkins_war(path, "lts")
    
    #home = os.path.join(os.getcwd(), "empty home")
    #print ("starting jenkins")
    #p = start_jenkins(war_file, home)
    #p.terminate()
    #print ("Done")
    pass
