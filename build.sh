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
	python setup.py --long-description | rst2html.py > pypi_homepage.html 2>>"$log_folder/make_docs.log"
}

run_tests()
{
	# runs automated tests
	echo "Running tests"
	py.test --cov pyjen ./unit_tests/test*.py --verbose --junit-xml test_results.xml > "$log_folder/pytest.log" 2>&1
	result=$?
	test $result -ne 0 && echo "Tests completed with errors" || echo "Tests completed successfully"
	return $result
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
	# PyPI and GitHub
	echo "Publishing release artifacts"

	# Publish API docs to thefriendlycoder.com
	ncftpput -R -v -m pyjentfc /PyJen ./docs/build/html/*
}
if [ -z "$@" ]; then
	echo "Usage: $0 <option>"
	echo
	echo "Where <option> is one of the following:"
	echo "     test"
	echo "     stat"
	echo "     docs"
	echo "     pack"
	echo "     publish"
	exit 0
fi

for param in "$@"
do
	case "$param" in
		test)
			run_tests
		;;

		stat)
			code_analysis
			if [ $? -ne 0 ]; then
				echo "code analysis detected problems"
				exit 1
			fi
		;;

		docs)
			make_docs
			if [ $? -ne 0 ]; then
				echo "Failed to generate API documentation"
				exit 1
			fi
		;;

		pack)
			create_package
			if [ $? -ne 0 ]; then
				echo "Failed to create redistributable package"
				exit 1
			fi
		;;

		publish)
			publish
			if [ $? -ne 0 ]; then
				echo "Failed to publish artifacts"
				exit 1
			fi
		;;

	esac
done
