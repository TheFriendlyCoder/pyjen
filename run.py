#Version-safe import of the 'print()' function
from __future__ import print_function
import argparse
import os
import logging
import subprocess
import shutil
import sys

# List of packages needed when building sources for pyjen
REQUIREMENTS = ['requests>=2.0.1', 'six', 'wheel', 'sphinx>=1.2.3', 'pytest', 'pytest-cov', 'mock', 'radon', 'pylint']

# Folder where log files will be stored
log_folder = os.path.abspath(os.path.join(os.path.curdir, "logs"))

# Set a global logger for use by this script
modlog = logging.getLogger('pyjen')
modlog.addHandler(logging.NullHandler())


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

    # delete any pre-existing packages
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # create new package
    modlog.info("creating package...")

    try:
        distobj = run_setup("setup.py", ["-q", "bdist_wheel"])
        distobj.run_commands()
    except Exception as err:
        modlog.error("Failed to generate wheel file")
        modlog.error(err)
        exit(1)

    # delete intermediate folders
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

    # todo: test package
    # pushd functional_tests > /dev/null
    # ./package_tests.sh

    modlog.info("package created successfully")


def _publish():
    """Publishes a PyJen release to PyPi"""
    modlog.info("publishing release...")

    try:
        result = subprocess.check_output(["python", "setup.py", "bdist_wheel", "upload"],
                                     stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as err:
        modlog.error("Failed to publish new PyJen release ({0})".format(err.returncode))
        modlog.error(err.output)
        exit(1)
    modlog.debug(result)

    # todo: after the publish completes, auto-update the version number
    # todo: lay tag on release
    modlog.info("release published successfully")


def _code_analysis():
    """Generates code analysis reports and metrics on the PyJen sources"""
    modlog.info("Running code analysis tools...")

    # PyLint code analysis
    from pylint import epylint as lint

    # now we generate a pylint report in HTML format
    params = 'pyjen -f html'
    with open(os.path.join(log_folder, "pylint.html"), "w") as std:
        with open(os.path.join(log_folder, "pylint_html_err.log"), "w") as err:
            lint.py_run(params, stdout=std, stderr=err, script="pylint")

    # next we generate a pylint report in 'parseable' format, for use on build automation
    params = 'pyjen'
    with open(os.path.join(log_folder, "pylint.txt"), "w") as std:
        with open(os.path.join(log_folder, "pylint_plain_err.log"), "w") as err:
            lint.py_run(params, stdout=std, stderr=err, script="pylint")

    modlog.info("Lint analysis can be found in ./" + os.path.relpath(log_folder, os.getcwd()) + "/pylint.html")

    # generate cyclomatic complexities for source files in XML format for integration with external tools
    pyjen_path = os.path.join(os.getcwd(), "pyjen")
    try:
        result = subprocess.check_output(["radon", "cc", "-sa", "--xml", pyjen_path],
                                     stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as err:
        modlog.error("Failed to calculate cyclomatic complexity ({0})".format(err.returncode))
        modlog.error(err.output)
        exit(1)
    complexity_log_filename = os.path.join(log_folder, "radon_complexity.xml")
    with open(complexity_log_filename, "w") as complexity_log_file:
        complexity_log_file.write(result)

    # next run all code analysers against all source files
    stats_log_filename = os.path.join(log_folder, "stats_cc.log")
    with open(stats_log_filename, "w") as stats_log:
        for (folder, subfolders, files) in os.walk(pyjen_path):
            for cur_file in files:
                if os.path.splitext(cur_file)[1] == ".py":
                    cur_file_full_path = os.path.join(folder, cur_file)
                    try:
                        result = subprocess.check_output(["radon", "cc", "-sa", cur_file_full_path],
                                                     stderr=subprocess.STDOUT, universal_newlines=True)
                    except subprocess.CalledProcessError as err:
                        modlog.error("Failed to calculate cyclomatic complexity ({0})".format(err.returncode))
                        modlog.error(err.output)
                        exit(1)
                    modlog.debug(result)
                    stats_log.write(result)

    stats_log_filename = os.path.join(log_folder, "stats_raw.log")
    with open(stats_log_filename, "w") as stats_log:
        for (folder, subfolders, files) in os.walk(pyjen_path):
            for cur_file in files:
                if os.path.splitext(cur_file)[1] == ".py":
                    cur_file_full_path = os.path.join(folder, cur_file)
                    try:
                        result = subprocess.check_output(["radon", "raw", "-s", cur_file_full_path],
                                                     stderr=subprocess.STDOUT, universal_newlines=True)
                    except subprocess.CalledProcessError as err:
                        modlog.error("Failed to calculate raw code statistics ({0})".format(err.returncode))
                        modlog.error(err.output)
                        exit(1)
                    modlog.debug(result)
                    stats_log.write(result)

    stats_log_filename = os.path.join(log_folder, "stats_mi.log")
    with open(stats_log_filename, "w") as stats_log:
        for (folder, subfolders, files) in os.walk(pyjen_path):
            for cur_file in files:
                if os.path.splitext(cur_file)[1] == ".py":
                    cur_file_full_path = os.path.join(folder, cur_file)
                    try:
                        result = subprocess.check_output(["radon", "mi", "-s", cur_file_full_path],
                                                     stderr=subprocess.STDOUT, universal_newlines=True)
                    except subprocess.CalledProcessError as err:
                        modlog.error("Failed to calculate maintainability index ({0})".format(err.returncode))
                        modlog.error(err.output)
                        exit(1)
                    modlog.debug(result)
                    stats_log.write(result)

    modlog.info("Radon analysis can be found here: ./" + os.path.relpath(log_folder, os.getcwd()) + "/stats*.log")
    modlog.info("Code analysis complete")


def _run_tests(RunFuncTests):
    """Runs all PyJen tests

    Generates reports about test coverage and such, storing the results in to disk

    :param bool RunFuncTests: indicates whether the functional tests should be run as well as the unit tests
    """
    modlog.info("running unit tests...")

    import pytest

    # TODO: Customize parameters based on user input, like verbosity level which shows all tests and reports
    #       ie: --cov-report term-missing, -r xEXw
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

    import sys
    if (3, 0) <= sys.version_info[:2] < (3, 3):
        p_ver = _version_tuple_to_string(sys.version_info[:3])
        modlog.info("Sphinx documentation tool does not support Python v{0}".format(p_ver))
        exit(1)

    if _get_package_version("Sphinx") < (1, 2, 3):
        modlog.error("Unsupported Sphinx version detected: " + _get_package_version("Sphinx"))
        modlog.error("Please run the --prep_env operation to property configure your environment.")
        exit(1)

    source_dir = os.path.join(os.getcwd(), "docs", "source")

    # TODO: Find a way to reduce the verbosity of the output

    # First we make sure the API docs are up to date
    try:
        from sphinx import apidoc
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
        shutil.rmtree(build_dir)

    # Generate the full online documentation in HTML format
    from distutils.core import run_setup
    try:
        # NOTE: default sphinx parameters are auto-loaded from the setup.cfg file
        distobj = run_setup("setup.py", ["build_sphinx"])
        distobj.run_commands()
    except Exception as err:
        modlog.error("Failed to generate online documentation")
        modlog.error(err)
        exit(1)

    # Generate a sample of the PyPI home page from the readme.rst file
    from docutils.core import publish_string
    readme_content = open('README.rst').read()
    homepage_html = publish_string(readme_content, writer_name='html')
    with open("pypi_homepage.html", "w") as outfile:
        outfile.write(homepage_html.decode("utf-8"))

    # TODO: Optionally open the prototype homepage in the default browser
    # TODO: Optionally open the index.html for the online docs in default browser
    modlog.info("Documentation complete")


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
    
    console_log_format = "%(asctime)s: %(message)s"
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
    _parser.add_argument('-s', '--stats', action='store_true', help='Run static code analysis again PyJen sources')
    _parser.add_argument('-u', '--publish', action='store_true', help='Publish release artifacts online to PyPI')
    _parser.add_argument('-t', '--test', action='store_true', help='Runs the suite of unit tests and generates metrics about the tests')
    _parser.add_argument('-f', '--functional_test', action='store_true', help='Runs the more time consuming functional test suite')
    _parser.add_argument('-d', '--docs', action='store_true', help='Generate online documentation for the project')
    # TODO: Consider using this to invoke a function when option is specified: parser.set_defaults(function)

    # If no command line arguments provided, display the online help and exit
    if len(sys.argv) == 1:
        _parser.print_help()
        sys.exit(0)
        
    _args = _parser.parse_args()
    modlog.debug("Command line params: " + str(_args))
    
    return _args


def main():
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

    if args.stats:
        _code_analysis()

    if args.publish:
        _publish()

if __name__ == "__main__":
    _configure_logger()
    main()
    # _show_version()
    # _prepare_env()
    # _make_package()
    # _make_docs()
