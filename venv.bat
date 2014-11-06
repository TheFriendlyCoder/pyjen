@if "%~1" == "" goto usage
@if not exist logs mkdir logs

:: Make sure we aren't currently running in a virtual environment
@if defined VIRTUAL_ENV call deactivate

:: See if we have pip installed
@where pip > nul 2>&1
@if errorlevel 1 goto missing_pip

:: See if we have virtualenv installed
@for /F "delims===" %%i in ('pip freeze -l') do @(
if "%%i" == "virtualenv" goto found
)
@pip install virtualenv
:found

:: create and activate our virtualenv
@if not exist py%~1 virtualenv -p %~1 .\py%~1 > .\logs\venv.log 2>&1
@if errorlevel 1 goto venv_failed
@call .\py%~1\scripts\activate.bat >> .\logs\venv.log 2>&1
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.
@goto :eof



:: --------------------- ERROR HANDLERS
:usage
@echo Usage: %~0 [version]
@echo.
@echo       ---- [version] is one of '2' or '3'
@exit /B

:missing_pip
@echo Python package manager (PIP) not found.
@exit /B 1

:venv_failed
@echo Failed to generate virtual environment
@exit /B 2