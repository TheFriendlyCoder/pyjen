#!/bin/bash

#war file to launch
JENKINS_WAR_FILE=jenkins1.541.war

#redirect the Jenkins home folder to a sub-folder
#under the current working directory named the same
#name as the war file and with a 'home' suffix
#eg: ./jenkins1.541home
JENKINS_HOME=${JENKINS_WAR_FILE%.*}home

#Sanity Check: Make sure the specified war file exists
if [ ! -f "$JENKINS_WAR_FILE" ]
  then
	echo "Jenkins war file not found: $JENKINS_WAR_FILE"
	exit 10
fi

#Make sure the Jenkins home folder exists
if [ ! -d "$JENKINS_HOME" ]; then
   mkdir "$JENKINS_HOME"
fi

#Now launch Jenkins
java -DJENKINS_HOME=$PWD/$JENKINS_HOME -jar $JENKINS_WAR_FILE
