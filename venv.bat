@echo off
virtualenv -p 3 .\py3 > venv.log 2>&1
call .\py3\scripts\activate.bat >> venv.log 2>&1
pip install requests wheel sphinx pylint pytest pytest-cov mock >> venv.log 2>&1
echo "Python virtual environment successfully configured. Run 'deactivate' to restore environment.