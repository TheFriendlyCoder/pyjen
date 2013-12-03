#!/bin/bash

#war file to launch
JENKINS_WAR_FILE=jenkins.war

#Home folder which should be redirected to a local sub-folder
JENKINS_HOME=.jenkins

#Sanity Check: Make sure the specified war file exists
if [ ! -f "$JENKINS_WAR_FILE" ]
  then
	echo "Jenkins war file not found: $JENKINS_WAR_FILE"
	exit 10
fi

#Now launch Jenkins
java -DJENKINS_HOME=$PWD/$JENKINS_HOME -jar $JENKINS_WAR_FILE
