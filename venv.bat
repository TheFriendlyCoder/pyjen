@if "%~1" == "" goto usage
@if not exist logs mkdir logs

:: Make sure we aren't currently running in a virtual environment
@if defined VIRTUAL_ENV call deactivate

:: Make sure pip is installed
@python -m pip --version > nul 2>&1
@if errorlevel 1 goto missing_pip

:: Make sure the virtualenv package is installed
@call:install_venv
@if errorlevel 1 goto venv_install_failed

:: create and activate our virtualenv
@if not exist py%~1 python -m virtualenv -p %~1 .\py%~1 > .\logs\venv.log 2>&1
@if errorlevel 1 goto venv_failed
@call .\py%~1\scripts\activate.bat >> .\logs\venv.log 2>&1
@echo Python virtual environment successfully configured. Run 'deactivate' to restore environment.
@exit /b 0


:: --------------------- FUNCTIONS
:: Confirms that the virtualenv package is installed
:install_venv
	@for /F "delims===" %%i in ('python -m pip freeze -l') do @(
		if "%%i" == "virtualenv" goto :eof
	)

	@echo installing venv
	@python -m pip install virtualenv
	@exit /b


:: --------------------- ERROR HANDLERS
:usage
@echo Usage: %~0 [version]
@echo.
@echo       ---- [version] is one of '2' or '3'
@exit /B

:missing_pip
@echo Python package manager (PIP) not found.
@exit /B 1

:venv_install_failed
@echo Failed to install te virtualenv package
@exit /B 2

:venv_failed
@echo Failed to generate virtual environment
@exit /B 3
