@if "%~1" == "" goto usage
@if not exist logs mkdir logs
:: Make sure we aren't currently running in a virtual environment
@if defined VIRTUAL_ENV (
	@echo Deactivating current venv
	call deactivate
)

:: See if we can use the 'py' launcher. If not default to the global python interpreter.
@if defined py_cmd set py_cmd=
@where py.exe > nul
@if errorlevel 1 (
	@where python.exe > nul
	@if errorlevel 1 goto :no_python
	@set py_cmd=python -m virtualenv -%~1
)
@if not defined py_cmd (
	@set py_cmd=py -%~1 -m virtualenv
)

:: create and activate our virtualenv
@if not exist py%~1 (
	@echo Constructing a new venv environment...
	@%py_cmd% .\py%~1 > .\logs\venv.log 2>&1
)
@if errorlevel 1 goto venv_failed

@echo Activating environment...
@call .\py%~1\scripts\activate.bat >> .\logs\venv.log 2>&1
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.
@exit /b 0

:: --------------------- ERROR HANDLERS
:usage
@echo Usage: %~0 [version]
@echo.
@echo       ---- [version] is one of '2' or '3'
@exit /B

:venv_failed
@echo Failed to generate virtual environment
@exit /B 3

:no_python
@echo Unable to locate a Python interpreter. Please check environment.
@exit /B 4