#Version-safe import of the 'print()' function
from __future__ import print_function
import argparse
import os
import logging
import shutil
import sys
from io import StringIO
try:
    # Make sure colored console output works on all platforms, but only when colorama and colorlog are installed
    import colorama
    from colorlog import ColoredFormatter
    colorama.init()
    ENABLE_COLOR = True
except ImportError:
    ENABLE_COLOR = False
# todo: make script work on Pyton 2
# todo: test scripts on Linux
# todo: have logger prepend name of function to messages

if sys.version_info >= (3, 4, 0):
    from contextlib import redirect_stdout
else:
    class redirect_stdout:
        """Context manager for temporarily redirecting stdout to another file

        based on redirect_stdout from contextlib"""

        def __init__(self, new_target):
            self._new_target = new_target
            # We use a list of old targets to make this CM re-entrant
            self._old_targets = []

        def __enter__(self):
            self._old_targets.append(sys.stdout)
            sys.stdout = self._new_target
            return self._new_target

        def __exit__(self, exctype, excinst, exctb):
            sys.stdout = self._old_targets.pop()

# List of packages needed when building sources for pyjen
# packages needed to use pyjen
PYJEN_PACKAGES = ['requests>=2.0.1', 'six']
# packages needed to build and test sources
SOURCE_PACKAGES = ['wheel', 'sphinx>=1.2.3', 'pytest', 'pytest-cov', 'mock', 'radon', 'pylint']
# nice-to-have packages that make it easier to work with pyjen sources
OPTIONAL_PACKAGES = ['colorlog', 'colorama', 'virtualenv']

REQUIREMENTS = PYJEN_PACKAGES
REQUIREMENTS.extend(SOURCE_PACKAGES)
REQUIREMENTS.extend(OPTIONAL_PACKAGES)

# Folder where log files will be stored
log_folder = os.path.abspath(os.path.join(os.path.curdir, "logs"))

# Set a global logger for use by this script
modlog = logging.getLogger('pyjen')
modlog.addHandler(logging.NullHandler())


class redirect_stderr:
    """Context manager for temporarily redirecting stderr to another file

    based on redirect_stdout from contextlib"""

    def __init__(self, new_target):
        self._new_target = new_target
        # We use a list of old targets to make this CM re-entrant
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(sys.stdout)
        sys.stderr = self._new_target
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        sys.stderr = self._old_targets.pop()


def _version_string_to_tuple(version):
    """Helper function that converts a version number from string format to a tuple

    :return: tuple of version numbers
    :rtype: :func:`tuple`
    """
    return tuple([int(i) for i in version.split(".")])
    pass


def _version_tuple_to_string(version):
    """Helper function that converts a version number from a tuple to string format

    :return: string representation of a version tuple
    :rtype: :func:`str`
    """
    return ".".join(list(map(str, version)))


def _get_package_version(package_name):
    """Helper function that returns the version number for a given Python package

    :param str package_name: the name of the package to query
    :return: The version of the given package as a tuple
    :rtype: :func:`tuple`
    """
    import pip
    installed_packages = pip.get_installed_distributions()
    for i in installed_packages:
        if i.key.lower() == package_name.lower():
            return _version_string_to_tuple(i.version)

    raise RuntimeError("Missing required package " + package_name)


def _split_requirement(package_requirement):
    """Helper function to extract the package name and required version from a package string

    :param str package_requirement: package requirement string, typically including a name and optional
        required version number, of the form 'package_name >= 1.2.3'
    :return: The name of the required package and its supported version number
    :rtype: :class:`tuple`
    """
    import re
    temp = re.split("<|>|=", package_requirement)
    package_name = temp[0]
    if len(temp) > 1:
        package_version = _version_string_to_tuple(temp[-1])
    else:
        package_version = ()

    return package_name, package_version


def _get_new_pyjen_version():
    """Calculates new version number for the PyJen package

    :returns: new version number
    :rtype: :func:`str`
    """
    import pyjen
    old_version = pyjen.__version__
    old_digit = old_version.split(".")
    return "{0}.{1}.{2}.{3}".format(old_digit[0], old_digit[1], int(old_digit[2])+1, old_digit[3])


def _update_pyjen_version():
    """Updates the minor version of the PyJen package in the init.py"""
    import fileinput
    import pyjen
    old_version = pyjen.__version__
    new_version = _get_new_pyjen_version()

    with fileinput.FileInput("./pyjen/__init__.py", inplace=True) as file:
        for line in file:
            print(line.replace(old_version, new_version), end='')


def _prepare_env():
    """Adds all PyJen dependencies to the Python runtime environment used to call this script

    Uses the global REQUIREMENTS list to install packages
    """
    try:
        import pip
    except ImportError:
        pip_url = "http://pip.readthedocs.org/en/latest/installing.html"
        modlog.error("PIP package not installed. See this website for details on how to install it: " + pip_url)
        exit(1)

    required_packages = REQUIREMENTS

    # Construct a list of arguments to pass to the PIP tool
    pip_args = []

    # See if any web proxy is enabled on the system and use it if found
    if 'http_proxy' in os.environ:
        proxy = os.environ['http_proxy']
        pip_args.append('--proxy')
        pip_args.append(proxy)
        modlog.info("Using the following proxy server: " + proxy)

    # Setup install command to install all missing packages
    pip_args.append('install')

    for req in required_packages:
        pip_args.append(req)

    # Configure PIP to do a silent install to avoid overly verbose output on the command line
    pip_args.append('--quiet')

    pip_error_log = os.path.join(log_folder, "pip_error.log")
    pip_args.append('--log-file')
    pip_args.append(pip_error_log)

    # Enable the following to debug package installation problems
    # pip_args.append('--no-cache')

    # Finally, run the installation process
    modlog.info('installing dependencies...')
    try:
        # HACK: PyLint has a transitive dependency on 'wrapt' and this package has some bugs which
        #       can prevent it from being installed on Windows platforms without Visual Studio
        #       Setting this environment variable disables all native, compiled code modules from this
        #       lib allowing it to be installed consistently.
        os.environ["WRAPT_EXTENSIONS"] = "FALSE"
        retval = pip.main(pip_args)
        if retval != 0:
            modlog.error("Error installing packages. See {0} for details.".format(pip_error_log))
            exit(1)

    except Exception as err:
        modlog.error("Error installing packages. See {0} for details.".format(pip_error_log))
        modlog.error(err)
        exit(1)

    modlog.info("All dependencies installed successfully")


def _show_version():
    """Shows the PyJen version number"""
    from pyjen import __version__
    modlog.info("PyJen Version " + __version__)


def _make_package():
    """Creates the redistributable package for the PyJen project"""
    import re
    from distutils.core import run_setup

    modlog.info("creating package...")

    # delete any pre-existing packages
    if os.path.exists("dist"):
        modlog.debug("Cleaning old package - ./dist")
        shutil.rmtree("dist")

    # create new package
    try:
        modlog.debug("Building package using distutils")
        distobj = run_setup("setup.py", ["-q", "bdist_wheel"])
        distobj.run_commands()
    except Exception as err:
        modlog.error("Failed to generate wheel file")
        modlog.error(err)
        exit(1)

    # delete intermediate folders
    modlog.debug("Purging intermediate package folders")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("pyjen.egg-info"):
        shutil.rmtree("pyjen.egg-info")

    # sanity check: make sure wheel file exists
    if not os.path.exists("dist"):
        modlog.error("Package folder ./dist not found. Package operation must have failed.")
        sys.exit(1)

    package_contents = os.listdir("dist")
    if len(package_contents) > 1:
        modlog.warning("Multiple files detected in package folder. Only one .whl file expected.")

    wheel_file_found = False
    wheel_file_pattern = r"^pyjen.*-py2.py3-none-any.whl$"
    for obj in package_contents:
        file_path = os.path.join(os.getcwd(), "dist", obj)
        if os.path.isfile(file_path) and re.search(wheel_file_pattern, obj) is not None:
            wheel_file_found = True

    if not wheel_file_found:
        modlog.error("Expected output file (.whl) not found in ./dist folder.")
        sys.exit(1)

    # TODO: test package
    # pushd functional_tests > /dev/null
    # ./package_tests.sh

    modlog.info("package created successfully")


def _publish():
    """Publishes a PyJen release to PyPi"""
    modlog.info("publishing release...")

    # TODO: lay tag on release

    from distutils.core import run_setup
    try:
        # NOTE: default sphinx parameters are auto-loaded from the setup.cfg file
        distobj = run_setup("setup.py", ["bdist_wheel", "upload"])
        distobj.run_commands()
    except Exception as err:
        modlog.error("Failed to upload new package to PyPI.")
        modlog.error(err)
        exit(1)

    _update_pyjen_version()
    # TODO: Commit change to init.py
    modlog.info("release published successfully")


def _run_pylint(on_ci):
    """Generates a PyLint static analysis report for the package

    :param bool on_ci: Indicates whether an automated tool is running this operation. Output will be customized for
                    machine readability
    """
    # PyLint code analysis
    from pylint import lint
    modlog.info("Running PyLint static analysis...")

    # setup our lint options
    params = ["pyjen"]
    if not on_ci:
        params.extend(["-f", "html"])  # parameters for user-friendly output

    if on_ci:
        pylint_report = os.path.join(os.getcwd(), "logs", "pylint_report.txt")   # plain-text output for automation
    else:
        pylint_report = os.path.join(os.getcwd(), "logs", "pylint_report.html")   # HTML output for humans to read

    pylint_log = os.path.join(os.getcwd(), "logs", "pylint.log")

    standard_output = StringIO()
    error_output = StringIO()
    with redirect_stdout(standard_output):
        with redirect_stderr(error_output):
            modlog.debug("Running pylint operation")
            lint_obj = lint.Run(params, exit=False)

    if 0 < lint_obj.linter.msg_status < 32:
        modlog.warning("PyLint defects detected (code {0})".format(lint_obj.linter.msg_status))
        modlog.warning("Check PyLint report in " + os.path.relpath(pylint_report))
    elif lint_obj.linter.msg_status == 0:
        modlog.info("PyLint analysis successful. No warnings detected.")
    else:
        modlog.info("PyLint analysis failed (code {0})".format(lint_obj.linter.msg_status))
        modlog.info("See log file for details " + os.path.relpath(pylint_log))

    modlog.debug("Writing log files")
    with open(pylint_report, "w") as fh:
        fh.write(standard_output.getvalue())
    with open(pylint_log, "w") as fh:
        fh.write(error_output.getvalue())
    standard_output.close()
    error_output.close()

    modlog.debug("Done running PyLint")
    # TODO: Optionally open the generated report in the default file viewer


def _run_complexity_analysis(on_ci):
    """Generates cyclomatic complexity reports for the package

    :param bool on_ci: Indicates whether an automated tool is running this operation. Output will be customized for
                    machine readability
    """
    modlog.debug("Running complexity analysis")

    # generate cyclomatic complexities for source files in XML format for integration with external tools
    pyjen_path = os.path.join(os.getcwd(), "pyjen")
    from radon.cli import cc

    # TODO: output in XML format when running on CI
    standard_output = StringIO()
    with redirect_stdout(standard_output):
        modlog.debug("Calling radon.cc")
        cc(paths=[pyjen_path], show_complexity=True, show_closures=True, total_average=True, xml=on_ci)

    modlog.debug("Writing report to disk")
    cc_report = os.path.join(log_folder, "radon_complexity.xml")
    with open(cc_report, "w") as fh:
        fh.write(standard_output.getvalue())
    standard_output.close()

    modlog.info("Cyclomatic complexity analysis complete. See " + os.path.relpath(cc_report))
    # TODO: Optionally open the generated report in the default file viewer


def _run_raw_analysis():
    """Generates raw code metrics for the package"""
    modlog.debug("Starting raw analysis")
    pyjen_path = os.path.join(os.getcwd(), "pyjen")
    from radon.cli import raw

    standard_output = StringIO()
    with redirect_stdout(standard_output):
        modlog.debug("Calling radon.raw")
        raw(paths=[pyjen_path], summary=True)

    modlog.debug("Writing report to disk")
    raw_report = os.path.join(log_folder, "raw_stats.txt")
    with open(raw_report, "w") as fh:
        fh.write(standard_output.getvalue())
    standard_output.close()

    modlog.info("Raw code metrics generated successfully. See " + os.path.relpath(raw_report))
    # TODO: Optionally open the generated report in the default file viewer


def _run_mi_analysis():
    """Generates maintainability index statistics for the package"""
    modlog.debug("Running maintainability index")
    pyjen_path = os.path.join(os.getcwd(), "pyjen")
    from radon.cli import mi

    standard_output = StringIO()
    with redirect_stdout(standard_output):
        modlog.debug("Calling radon.mi")
        mi(paths=[pyjen_path], show=True)

    modlog.debug("Writing report to disk")
    mi_report = os.path.join(log_folder, "mi_stats.txt")
    with open(mi_report, "w") as fh:
        fh.write(standard_output.getvalue())
    standard_output.close()

    modlog.info("Maintainability index metrics generated successfully. See " + os.path.relpath(mi_report))
    # TODO: Optionally open the generated report in the default file viewer


def _code_analysis(on_ci):
    """Generates code analysis reports and metrics on the PyJen sources

    :param bool on_ci: Indicates whether an automated tool is running this operation. Output will be customized for
                        machine readability
    """
    modlog.info("Running code analysis tools...")
    _run_pylint(on_ci)
    _run_complexity_analysis(on_ci)
    _run_raw_analysis()
    _run_mi_analysis()
    modlog.info("Code analysis complete")


def _run_tests(RunFuncTests):
    """Runs all PyJen tests

    Generates reports about test coverage and such, storing the results in to disk

    :param bool RunFuncTests: indicates whether the functional tests should be run as well as the unit tests
    """
    modlog.info("running unit tests...")

    import pytest

    test_params = ["./unit_tests"]
    if RunFuncTests:
        test_params.append("./functional_tests")
    test_params.extend(["-s", "-q",
                   "--cov-report", "html", "--cov-report", "xml", "--cov", "pyjen", "--no-cov-on-fail",
                   "--junit-xml", "test_results.xml"])

    # TODO: Find a way to suppress remaining output generated by this call
    pytest.main(test_params)

    modlog.info("finished running tests")


def _make_docs():
    """Generates the online documentation for the project"""
    modlog.info("Generating API documentation...")

    if _get_package_version("Sphinx") < (1, 2, 3):
        modlog.error("Unsupported Sphinx version detected: " + _get_package_version("Sphinx"))
        modlog.error("Please run the --prep_env operation to property configure your environment.")
        exit(1)

    source_dir = os.path.join(os.getcwd(), "docs")
    log_file = os.path.join(os.getcwd(), "logs", "sphinx.log")

    standard_output = StringIO()
    error_output = StringIO()

    # First we make sure the API docs are up to date
    try:
        from sphinx import apidoc
        with redirect_stdout(standard_output):
            with redirect_stderr(error_output):
                modlog.debug("Calling Sphinx to build API docs")
                # NOTE: The first parameter to main is assumed to be the name of the executable that called
                #       main, which in our case doesn't exist. So we give it an empty value
                return_code = apidoc.main(["", "--force", "--separate", "-o", source_dir, "pyjen"])

        if return_code is not None and return_code != 0:
            modlog.error("Failed to generate API docs ({0}).".format(return_code))
            exit(1)
    except Exception as err:
        modlog.error("Failed to generate API docs.")
        modlog.error(str(err))
        exit(1)

    # TODO: Do a git stat and if any file have been modified throw a warning to the user

    # Purge any previous build artifacts
    build_dir = os.path.join(os.getcwd(), "build", "sphinx")
    if os.path.exists(build_dir):
        modlog.debug("Purging Sphinx output folder")
        shutil.rmtree(build_dir)

    modlog.debug("Creating empty build folder")
    os.makedirs(build_dir)

    # Generate the full online documentation in HTML format
    from distutils.core import run_setup
    try:
        with redirect_stdout(standard_output):
            with redirect_stderr(error_output):
                modlog.debug("Calling setuptools to generate online docs")
                # NOTE: default sphinx parameters are auto-loaded from the setup.cfg file
                distobj = run_setup("setup.py", ["build_sphinx", "-q"])
                distobj.run_commands()
    except Exception as err:
        modlog.error("Failed to generate online documentation")
        modlog.error(err)
        exit(1)

    modlog.debug("Writing logs to disk")
    tmp_error_out = error_output.getvalue()
    if len(tmp_error_out) > 0:
        modlog.warning("Sphinx warnings detected. Check log file for details " + os.path.relpath(log_file, os.getcwd()))
    with open(log_file, mode='w') as fh:
        fh.write(standard_output.getvalue())
        fh.write(tmp_error_out)

    standard_output.close()
    error_output.close()
    # TODO: Optionally open the index.html for the online docs in default browser
    modlog.info("Documentation complete")


def _generate_homepage():
    modlog.debug("Generating sample PyPI homepage")
    # Generate a sample of the PyPI home page from the readme.rst file
    from docutils.core import publish_string
    readme_content = open('README.rst').read()
    homepage_html = publish_string(readme_content, writer_name='html')

    modlog.debug("Wriiting HTML file to disk")
    with open("pypi_homepage.html", "w") as outfile:
        outfile.write(homepage_html.decode("utf-8"))

    # TODO: Optionally open the prototype homepage in the default browser


def _configure_logger():
    """Configure the custom logger for this script

    All info messages and higher will be shown on the console
    All messages from all priorities will be streamed to a log file
    """
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    global modlog
    modlog = logging.getLogger("pyjen")
    modlog.setLevel(logging.DEBUG)

    # Primary logger will write all messages to a log file
    log_file = os.path.join(log_folder, "run.log")
    if os.path.exists(log_file):
        os.remove(log_file)
    file_logger = logging.FileHandler(log_file)
    file_logger_format = "%(asctime)s %(levelname)s:%(message)s"
    file_formatter = logging.Formatter(file_logger_format)
    file_logger.setFormatter(file_formatter)
    file_logger.setLevel(logging.DEBUG)

    modlog.addHandler(file_logger)

    # Secondary logger will show all 'info' class messages and below on the console
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)

    if ENABLE_COLOR:
        console_formatter = ColoredFormatter()
    else:
        console_log_format = "%(asctime)s: (%(levelname)s) %(message)s"
        console_formatter = logging.Formatter(console_log_format)
    console_formatter.datefmt = "%H:%M"
    console_logger.setFormatter(console_formatter)
    modlog.addHandler(console_logger)

    
def _get_args():
    """Configure the command line parser and online help systems

    :returns: set of parameters provided by the user on the command line
    """
    _parser = argparse.ArgumentParser(description='PyJen source project configuration utility')

    _parser.add_argument('-v', '--version', action='store_true', help='Display the PyJen version number')
    _parser.add_argument('-e', '--prep_env', action='store_true', help='Install all Python packages used by PyJen sources')
    _parser.add_argument('-p', '--package', action='store_true', help='Generate redistributable package for PyJen')
    _parser.add_argument('-s', '--stats', action='store_true', help='Run static code analysis against PyJen sources')
    _parser.add_argument('-u', '--publish', action='store_true', help='Publish release artifacts online to PyPI')
    _parser.add_argument('-t', '--test', action='store_true', help='Runs the suite of unit tests and generates metrics about the tests')
    _parser.add_argument('-f', '--functional_test', action='store_true', help='Runs the more time consuming functional test suite')
    _parser.add_argument('-d', '--docs', action='store_true', help='Generate online documentation for the project')
    _parser.add_argument('--ci', action='store_true', help='Indicates an automated system is using the script. Output will assume machine readable format.')
    # TODO: Add a "verbose" output option, then all data typically streamed to log files is streamed to stdout

    # If no command line arguments provided, display the online help and exit
    if len(sys.argv) == 1:
        _parser.print_help()
        sys.exit(0)
        
    _args = _parser.parse_args()
    modlog.debug("Command line params: " + str(_args))
    
    return _args


def main():
    """Main entry point function"""
    args = _get_args()

    if args.prep_env:
        _prepare_env()

    if args.version:
        _show_version()

    if args.test or args.functional_test:
        _run_tests(args.functional_test)

    if args.package:
        _make_package()

    if args.docs:
        _make_docs()
        _generate_homepage()

    if args.stats:
        _code_analysis(args.ci)

    if args.publish:
        _publish()

if __name__ == "__main__":
    _configure_logger()
    main()
    # _show_version()
    # _prepare_env()
    # _make_package()
    # _make_docs()
    # print(_get_new_pyjen_version())
    # _publish()
    # _run_pylint()
    # _run_complexity_analysis()
    # _run_raw_analysis()
    #_run_mi_analysis()
