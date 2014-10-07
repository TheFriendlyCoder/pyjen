@echo off
if not exist logs mkdir logs
if not exist py3 pythono -m virtualenv -p 3 .\py3 > .\logs\venv.log 2>&1
if errorlevel 1 (
	@echo Failed to launch virtualenv
	exit /B 1
)
call .\py3\scripts\activate.bat >> .\logs\venv.log 2>&1
if errorlevel 1 (
	@echo Failed to activate virtualenv
	exit /B 1
)
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.