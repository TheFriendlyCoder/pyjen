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


class JenkinsProcess(object):
    def __init__(self, edition):
        assert edition == "lts" or edition == "latest"

        self._edition = edition

    def start(self, home_folder):
        """Attempts to launch an isolated instance of Jenkins for testing purposes

        This function will block until the instance of Jenkins is successfully
        loaded and ready for use by subsequent test logic

        :param str home_folder: path to the folder to be used as the Jenkins home folder
        """
        war_file = self._get_jenkins_war()
        print("starting jenkins...")
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
        JENKINS_PORT=random.randrange(1000, 1100)
        args.append("--httpPort={0}".format(JENKINS_PORT))

        #Now launch Jenkins in a secondary, non-blocking process
        jenkins_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

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
        print ("Jenkins started...")
        self._url = "http://localhost:{0}".format(JENKINS_PORT)
        self._process = jenkins_process

    @property
    def url(self):
        return self._url

    def terminate(self):
        self._process.terminate()

    def _get_jenkins_war(self):
        """Downloads the latest and LTS versions of the Jenkins WAR file

        if any .war files already exist in the target folder they will not
        be overwritten

        :return: path to the downloaded war file
        :rtype: :class:`str`
        """

        print("Getting Jenkins war")
        output_path = os.path.dirname(os.path.abspath(__file__))
        if self._edition == "lts":
            src_url = lts_url
            output_file = os.path.join(output_path, "jenkins_lts.war")
        else:
            src_url = latest_url
            output_file = os.path.join(output_path, "jenkins_latest.war")

        if not os.path.exists(output_file):
            urllib.urlretrieve(src_url, output_file, self._progress_hook)

        return output_file

    @staticmethod
    def _progress_hook(block_number, block_size, total_size):
        """Callback used by `func`:get_jenkins_wars to report the download progress
        :param int block_number: the current data block being downloaded
        :param int block_size: the size, in bytes, of each downloaded block
        :param int total_size: the total number of bytes being downloaded
        """
        if block_number == 0:
            JenkinsProcess._progress_hook.counter = 0
            #print ("10..", end="")
            sys.stdout.flush()
        total_blocks = math.ceil(total_size / block_size)

        percent_done = math.ceil(block_number / total_blocks * 100)

        increment = math.floor(percent_done / 10)
        if increment != JenkinsProcess._progress_hook.counter:
            msg = str(10-increment)
            if increment != 10:
                msg += ".."
            #print (msg, end="")
            sys.stdout.flush()
        JenkinsProcess._progress_hook.counter = increment


def safe_delete (path):
    """Recursively deletes the contents of a given folder, even when files are read only

    :param str path: root folder to be deleted
    """
    if not os.path.exists(path):
        return

    for root, dirs, files in os.walk(path):
        for fname in files:
            full_path = os.path.join(root, fname)
            os.chmod(full_path, stat.S_IWRITE)

    shutil.rmtree(path)

if __name__ == "__main__":

    home = os.path.join(os.getcwd(), "empty home")

    tester = JenkinsProcess("lts")

    print("starting jenkins")
    tester.start(home)
    print("started: " + tester.url)
    tester.terminate()
    print("Done")
    pass
