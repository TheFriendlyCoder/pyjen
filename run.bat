@setlocal
@echo off
set log_folder=%cd%/logs
if not exist "%log_folder%" mkdir "%log_folder%"

echo Running tests
py.test --cov-report term-missing --cov pyjen -s ./unit_tests --verbose --junit-xml test_results.xml > "%log_folder%/pytest.log" 2>&1
if not errorlevel 1 (
    echo Tests completed successfully
) else (
    echo Test failed. See %log_folder%/pytest.log for details.
)