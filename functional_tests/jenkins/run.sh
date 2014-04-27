#!/bin/bash

#config parameters for newest jenkins versioni
JENKINS_VERSION_NAME=jenkins_latest
#JENKINS_VERSION_NAME=jenkins_lts

JENKINS_WAR_FILE=$JENKINS_VERSION_NAME".war"
JENKINS_HOME=$JENKINS_VERSION_NAME"_home"

#Sanity Check: Make sure the specified war file exists
if [ ! -f "$JENKINS_WAR_FILE" ]
  then
	echo "Jenkins war file not found: $JENKINS_WAR_FILE"
	exit 10
fi

#Now launch Jenkins
java -DJENKINS_HOME=$PWD/$JENKINS_HOME -jar $JENKINS_WAR_FILE
