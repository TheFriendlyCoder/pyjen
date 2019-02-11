#!/bin/bash
# This is a helper script used to inject environment variables into the
# build environment, for use by the 'tox' build tool. See the tox.ini
# file for details

# Inject the project name into the environment, dynamically parsed from
# the project.prop file
export PROJECT_NAME=`python -c "import ast; print(ast.literal_eval(open('project.prop').read())['NAME'])"`
