#!/bin/bash
if [ ! -f jenkins_latest.war ]; then
	wget -O jenkins_latest.war http://mirrors.jenkins-ci.org/war/latest/jenkins.war;
fi

if [ ! -f jenkins_lts.war ]; then
	wget -O jenkins_lts.war http://mirrors.jenkins-ci.org/war-stable/latest/jenkins.war;
fi
