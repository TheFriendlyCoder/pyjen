#!/bin/bash
which pip > /dev/null
if [ $? -ne 0 ]
	then echo "ERROR: Python command line tool pip not found. Please check environment.";
	exit 1;
fi

pip freeze | grep virtualenv > /dev/null
if [ $? -ne 0 ]; then 
	pip install virtualenv
	if [ $? -ne 0]; then 
		echo "Error installing virtualenv dependency"
		exit 1;
	fi
fi

if [ ! -d py2 ]; then
	virtualenv --no-site-packages -p python2 py2;
	source py2/bin/activate;
	pip install requests wheel;
	if [ $? -ne 0 ]; then
		echo "Error installing requests dependency in virtualenv 2.x"
		exit 1;
	fi
	deactivate;
fi

if [ ! -d py3 ]; then
	virtualenv --no-site-packages -p python3 py3;
	source py3/bin/activate;
	pip install requests wheel;
	if [ $? -ne 0 ]; then
		echo "Error installing requests dependency in virtualenv 3.x"
		exit 1;
	fi
	deactivate;
fi
