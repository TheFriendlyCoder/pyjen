#!/bin/bash
# Linux configuration script that prepares the local build environment
#
# Run without any command line parameters to get usage information


# Helper function for setting up build environment for a particular 
# version of Python. It expects 2 input paramters:
#	$1 - executable for the python version to set up (e.g.: python3)
#	$2 - local folder, typically relative to the current path
#		to configure the virtualenv environment
function setup_venv {

	#check our input parameters
	test $# -ne 2 && { echo "incorrent number of paramters";return 1; }

	python_executable=$1
	local_path=$2

	python_version_string=$($python_executable --version 2>&1)
	echo "Configuring $python_version_string environment"

	#make sure a virtualenv for the specified version exists
	test ! -d "$local_path" && virtualenv --no-site-packages -p $python_executable $local_path
	
	#activate our virtualenv version
	source $local_path/bin/activate
	test $? -ne 0 && { echo "error activating Python virtualenv: $?"; return 2; }
}


# Helper function used to make sure the host Python environment
# is capable of setting up our environment (ie: making sure
# pip and virtualenv tools are available)
function prep_host_env {
	#Make sure PIP command line tool is installed
	which pip > /dev/null
	test $? -ne 0 && { echo "ERROR: Python command line tool pip not found. Please check environment."; return 1; }

	# See if virtualenv is installed, and download it if not
	pip freeze | grep virtualenv > /dev/null
	if [ $? -ne 0 ] 
	then 
		pip install virtualenv
		test $? -ne 0 && { echo "Error installing virtualenv dependency"; return 2; }
	fi
}

# Helper function that just shows the command line
# usage to stdout
function show_usage {
	echo "Usage:"
	echo "	  $BASH_SOURCE <python_version>"
	echo ""
	echo "    <python_version> - number indicating which python version to use"
	echo "                       valid values: 2 3"
	echo ""
	echo "example:"
	echo "    configure env for Python 3: $BASH_SOURCE 3"
	echo ""
	echo "tip: to have the new environment auto-activated"
	echo "     simply run this script in the active shell"
	echo "     using the '.' source operator, as in:"
	echo ""
	echo "        . $BASH_SOURCE 3"
	echo ""
	echo "    Alternatively, you can use the 'source' command:"
	echo ""
	echo "        source $BASH_SOURCE 3"
}

	

# Primary entry point
# this function performs the actual setup
# of the build environment
function main {
	echo "running main"
	test $# -ne 1 && { show_usage; return 0; }

	echo "checking venv"
	#check to see if we are already in a virtualenv environment
	#and deactivate it if we are
	test ! -z "$VIRTUAL_ENV" && deactivate
 
	echo "prepping host"
	# Prepare host environment
	prep_host_env
	test $? -ne 0 && return $?

	# Configure environment for requested Python version
	case $1 in
	2) 
		setup_venv python2 py2
		result=$? ;;
	3)
		setup_venv python3 py3
		result=$? ;;
	*)
		echo "Unsupported Python version $1"
		return 1;;
	esac
	
	test $result -ne 0 && return $result
	
	#Finally, make sure this projects folder is 
	#included on the pythonpath
	export PYTHONPATH=$PWD:$PYTHONPATH

	echo "Configuration complete. Run 'deactivate' to restore shell environment."
}



#############################################################
#Entry point
main $*
result=$?

# here we terminate the sub-shell used to launch this script
# with the appropriate error code
test "$0" == "${BASH_SOURCE[0]}" && exit $result

# if we make it here we know we are running under a
# 'source'd script that is running in the current
# session so we need to 'return' our result code
return $result

