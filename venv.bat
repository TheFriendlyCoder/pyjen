@echo off
if "%~1" == "" goto showusage
if not exist logs mkdir logs
if not exist py3 virtualenv -p c:\python34\python.exe .\py3 > .\logs\venv.log 2>&1
if errorlevel 1 exit /B
if not exist py2 virtualenv -p c:\python27\python.exe .\py2 >> .\logs\venv.log 2>&1
if errorlevel 1 exit /B

call .\%~1\scripts\activate.bat >> .\logs\venv.log 2>&1
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.
goto :EOF

:showusage
@echo Missing python interpreter parameter. Valid values are 'py2' and 'py3'
exit /B