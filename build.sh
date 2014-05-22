#!/bin/bash

# Linux script that runs all release prep operations on the library
# This includes generating API docs, running all unit tests, and
# generating a redistributable package.

log_folder=$PWD/logs
test -d "$log_folder" || mkdir -p "$log_folder"

make_docs()
{
	# Generates API documents for online reference pages

	echo "Making API docs"
	pushd ./docs/source > /dev/null
	#sphinx-apidoc -o . ../.. ../../unit_tests ../../functional_tests ../../setup.py > "$log_folder/make_docs.log" 2>&1
	sphinx-apidoc -o . ../../pyjen > "$log_folder/make_docs.log" 2>&1
	result=$?
	popd > /dev/null
	test $result -ne 0 && return $result
	pushd ./docs > /dev/null
	make html >> "$log_folder/make_docs.log" 2>&1
	result=$?
	popd > /dev/null
	test $result -ne 0 && return $result

	# for extra verification, lets generate a sample PyPI homepage
	python setup.py --long-description | rst2html.py > pypi_homepage.html
}

run_tests()
{
	# runs automated tests
	echo "Running tests"
	py.test ./unit_tests/test*.py --verbose --junit-xml test_results.xml > "$log_folder/pytest.log" 2>&1
}

create_package()
{
	# generates redistributable binary packages, such as a wheel file
	echo "Generating packages"
	python setup.py bdist_wheel > "$log_folder/package.log" 2>&1
	rm -rf ./build > /dev/null
}

code_analysis()
{
	# runs code analysis tools against project, such as PyLint
	echo "Running code analysis tools"
	#find -iname "*.py" | xargs pylint --rcfile=.pylint -f parseable > "$log_folder/pylint.log" 2>&1
}

publish()
{
	# Publishes built version to relevant sources, including
	# PyPI and GiHub
	echo "Publishing release artifacts"

	# Publish API docs to thefriendlycoder.com
	ncftpput -R -v -m pyjentfc /PyJen ./docs/build/html/*
}


run_tests
if [ $? -ne 0 ]; then
	echo "Unit test failures detected"
	exit 1
fi

code_analysis
if [ $? -ne 0 ]; then
	echo "code analysis detected problems"
	exit 1
fi

make_docs
if [ $? -ne 0 ]; then
	echo "Failed to generate API documentation"
	exit 1
fi

create_package
if [ $? -ne 0 ]; then
	echo "Failed to create redistributable package"
	exit 1
fi

#publish
