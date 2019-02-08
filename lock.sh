#!/bin/bash -e
virtualenv -p python2 tmp > /dev/null
source ./tmp/bin/activate
pip install -e .[dev] > /dev/null
pip freeze --exclude-editable > requirements2.txt
deactivate
rm -rf tmp > /dev/null

virtualenv -p python3 tmp > /dev/null
source ./tmp/bin/activate
pip install -e .[dev] > /dev/null
pip freeze --exclude-editable > requirements3.txt
deactivate
rm -rf tmp > /dev/null
