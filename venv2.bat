@echo off
if not exist logs mkdir logs
if not exist py2 virtualenv -p 2 .\py2 > .\logs\venv.log 2>&1
call .\py2\scripts\activate.bat >> .\logs\venv.log 2>&1
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.