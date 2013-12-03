@setlocal
@echo off
set JENKINS_HOME=%CD%/.jenkins
set JENKINS_WAR_FILE=jenkins.war

java -DJENKINS_HOME="%JENKINS_HOME%" -jar %JENKINS_WAR_FILE%