#!/bin/bash

# sets up build environment for a particular version of Python
setup_env()
{
	if [ -z "$1" ] || [ -z "$2" ]; then echo "missing parameter"; exit 1; fi
	python_ver=$1
	local_path=$2

	#make sure a virtualenv for the specified version exists
	if [ ! -d "$local_path" ]; then
		virtualenv --no-site-packages -p $python_ver $local_path
	fi
	
	#make sure the env is configured correctly
	source $local_path/bin/activate
	pip install -U requests wheel docutils sphinx pylint pytest
	if [ $? -ne 0 ]; then
		echo "Error installing dependency in virtualenv $local_path"
		exit 1;
	fi
}

if [ -z "$1" ]; then
	echo "Usage:"
	echo "	$0 python_version"
	echo ""
	echo "  python_version - number indicating which python version to use"
	echo "  valid values: 2 3"
	echo ""
	echo "example:"
	echo "  configure env for Python 3: $0 3"
	exit 1;
fi

#check to see if we are already in a virtualenv environment
#and deactivate it if we are
if [ ! -z "$VIRTUAL_ENV" ]; then
	deactivate
fi
 
#Make sure PIP command line tool is installed
which pip > /dev/null
if [ $? -ne 0 ]
	then echo "ERROR: Python command line tool pip not found. Please check environment.";
	exit 1;
fi

# See if virtualenv is installed, and download it if not
pip freeze | grep virtualenv > /dev/null
if [ $? -ne 0 ]; then 
	pip install virtualenv
	if [ $? -ne 0]; then 
		echo "Error installing virtualenv dependency"
		exit 1;
	fi
fi

# Configure environment for requested Python version
case $1 in
2)
	echo "Configuring Python v2 environment..."
	setup_env python2 py2
	;;
3)
	echo "Configuring Python v3 environment..."
	setup_env python3 py3
	;;
*)
	echo "Unsupported Python version $1"
	exit 1
	;;
esac
