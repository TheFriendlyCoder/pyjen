#!/bin/bash
which pip > /dev/null
if [ $? -ne 0 ]
	then echo "ERROR: Python command line tool pip not found. Please check environment.";
	exit 1;
fi

pip freeze | grep virtualenv > /dev/null
if [ $? -ne 0 ] 
	then pip install virtualenv
fi

if [ ! -d py2 ]; then
	virtualenv --no-site-packages -p python2 py2;
	source py2/bin/activate;
	pip install requests;
	deactivate;
fi

if [ ! -d py3 ]; then
	virtualenv --no-site-packages -p python3 py3;
	source py3/bin/activate;
	pip install requests;
	deactivate;
fi
