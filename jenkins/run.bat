@setlocal
@echo off
set JENKINS_HOME_FOLDER=jenkins1.541home
set JENKINS_WAR_FILE=jenkins1.541.war

java -DJENKINS_HOME=%CD%/%JENKINS_HOME_FOLDER% -jar %JENKINS_WAR_FILE%