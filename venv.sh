virtualenv --no-site-packages -p python2 py2
virtualenv --no-site-packages -p python3 py3
source py2/bin/activate
pip install requests
deactivate

source py3/bin/activate
pip install requests
deactivate
