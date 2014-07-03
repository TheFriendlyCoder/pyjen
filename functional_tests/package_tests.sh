#!/bin/bash

main()
{
	# setup our environment
	test -d "./py3" && rm -rf ./py3
	virtualenv --no-site-packages -p python3 ./py3
	source ./py3/bin/activate

	# create a local cache of the pyjen dependencies
	# TODO: find a way to get the set of dependencies from the latest
	#		build of pyjen rather than the default live version on pypi
	test -d "./cache" && rm -rf ./cache 
	mkdir ./cache
	pip install --download ./cache requests
	result=$?
	test $result -ne 0 && return $result

	ls ../dist/*.whl > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "Python wheel file not found" 
		return 1
	fi
	cp ../dist/*.whl ./cache
	result=$?
	test $result -ne 0 && return $result

	# Finally, try doing the install and make sure it worksi
	pip install --pre --no-index --log ./pip.log --find-links ./cache pyjen
}

main
result=$?
if [ $result -ne 0 ]; then
	echo "Package tests failed $result"
else
	echo "Package tests succeeded"
fi
exit $result
