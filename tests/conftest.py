import os
import shutil
import tarfile
import pytest
import logging
import warnings
import docker
import multiprocessing
import inspect
from pathlib import Path
from pyjen.jenkins import Jenkins
from .jenkins_manager import JenkinsManager


# Boolean flag indicating whether or not a Dockerized test environment should
# be used. See the pytest_collection_modifyitems helper for details
NEEDS_DOCKER = False

# Default Docker container to use for testing
# May be overloaded from the command prompt using '--jenkins-version'
DEFAULT_JENKINS_VERSION = "jenkins/jenkins:2.345-alpine"

# Global flag used to see whether we've already attempted to run our Jenkins
# containerized environment. Prevents redundant failures from slowing down
# the test runner
FAILED_DOCKER_SETUP = False

# List of Jenkins plugins to install in the test environment
# May include specific versions of plugins using the notation 'plugin:version'
# See the docs on how to use the Jenkins docker container for details:
#       https://github.com/jenkinsci/docker/blob/master/README.md
JENKINS_PLUGINS = [
    # Jenkins "pipeline" pseudo-plugin that installs all dependencies to run
    # Jenkins pipeline scripts. Needed by many "core" plugins as well like
    # Git.
    "workflow-aggregator",

    # Needed to test SCM related operations in the core API
    "git",

    # Needed to test PyJen plugins that ship with the core framework
    "nested-view",
    "sectioned-view",
    "conditional-buildstep",
    "parameterized-trigger",
    "build-blocker-plugin",
    "jenkins-multijob-plugin",
    "artifactdeployer",
    "flexible-publish",
]


def pytest_addoption(parser):
    """Customizations for the py.test command line options"""
    parser.addoption(
        "--skip-docker",
        action="store_true",
        help="don't run tests that depend on the Jenkins service"
    )
    parser.addoption(
        "--preserve",
        action="store_true",
        help="Keeps the Docker container used for testing alive after the "
             "test run has completed"
    )
    parser.addoption(
        "--regenerate",
        action="store_true",
        help="Regenerates the stored HTTP responses used by the tests"
    )
    parser.addoption(
        "--jenkins-version",
        action="store",
        default=DEFAULT_JENKINS_VERSION,
        help="Name of docker container for the Jenkins version to test against"
    )


def _workspace_dir():
    """
    Returns:
        str: the absolute path to the root folder of the workspace
    """
    cur_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(cur_path, ".."))


def docker_logger(container_id):
    """Helper method that redirects Docker logs to Python logger

    This helper method is intended to be used as a background daemon to
    redirect all log messages from a given Docker container to the Python
    logging subsystem.

    Args:
        container_id (str): ID for the container to check logs for
    """
    log = logging.getLogger(__name__)
    client = docker.APIClient(version="auto")
    for cur_log in client.logs(container_id, stream=True, follow=True):
        log.debug(cur_log.decode("utf-8").strip())


@pytest.fixture(scope="session", autouse=True)
def configure_logger():
    """Configure logging for the test runner"""
    log_dir = os.path.join(_workspace_dir(), "logs")
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    global_log = logging.getLogger()
    global_log.setLevel(logging.DEBUG)

    verbose_format = "%(asctime)s(%(levelname)s->%(module)s):%(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(verbose_format, date_format)
    file_handler = logging.FileHandler(
        os.path.join(log_dir, "tests.log"),
        mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    global_log.addHandler(file_handler)
    # Disable distutils warnings produced by the Python Docker library
    warnings.filterwarnings("ignore", ".*distutils.*")


@pytest.fixture(scope="session")
def jenkins_env(request, configure_logger):
    """Fixture that generates a dockerized Jenkins environment for testing"""
    global FAILED_DOCKER_SETUP
    log = logging.getLogger(__name__)

    if FAILED_DOCKER_SETUP:
        raise Exception(
            "Skipping Docker setup logic. Previous attempt failed.")

    if not NEEDS_DOCKER:
        data = {
            "url": "http://localhost",
            "admin_user": "admin",
            "admin_token": "password",
            "plugins": JENKINS_PLUGINS[:],
        }
        yield data
        return

    image_name = request.config.getoption("--jenkins-version")
    log.info("Using Jenkins docker container '{0}'".format(image_name))
    preserve_container = request.config.getoption("--preserve")

    try:
        jk_env = JenkinsManager(image_name, JENKINS_PLUGINS)
    except Exception as err:
        FAILED_DOCKER_SETUP = True
        return

    jk_env.get_image()

    # create our docker container, if one doesn't already exist
    log.info("Creating Jenkins Docker container...")
    jk_env.create_container()

    try:
        # Setup background thread for redirecting log output to Python logger
        d = multiprocessing.Process(
            name='docker_logger',
            target=docker_logger,
            args=[jk_env.container_id]
        )
        d.daemon = True
        d.start()

        log.info("Starting Jenkins Docker container...")
        jk_env.launch_container()

        data = {
            "url": jk_env.url,
            "admin_user": jk_env.user,
            "admin_token": jk_env.password,
            "plugins": JENKINS_PLUGINS[:],
        }

        yield data
    finally:
        if preserve_container:
            return
        log.info("Shutting down Jenkins Docker container...")
        jk_env.stop_container()
        log.info("Done Docker cleanup")


@pytest.fixture(scope="function")
def jenkins_api(jenkins_env):
    """Test fixture that creates a connection to the Jenkins test server

    The API connection will use a basic-auth protocol using the connection
    parameters provided by the jenkins_env test fixture
    """
    jk = Jenkins.basic_auth(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))

    yield jk


def pytest_collection_modifyitems(config, items):
    """Applies command line customizations to filter tests to be run"""
    if not config.getoption("--skip-docker"):
        return

    skip_jenkins = pytest.mark.skip(reason="Skipping Jenkins Server tests")
    for item in items:
        if "jenkins_env" in item.fixturenames:
            item.add_marker(skip_jenkins)


@pytest.fixture(scope='module')
def vcr_config(request):
    # TODO: default to "none" if the block network access flag is passed
    #       or maybe only default to "once" if a test has no cassette at all
    record_mode = "rewrite" if request.config.getoption("--regenerate") else "once"
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [('authorization', 'DUMMY')],
        "record_mode": record_mode,
        # remove the "port" parameter from the match criteria so every time
        # we rerun these tests against a new container the cassettes will
        # still get matched properly
        "match_on": ['method', 'scheme', 'host', 'path', 'query'],
        "decode_compressed_response": True
    }


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    # Put all cassettes in ./tests/cassettes/{module}/{test}.yaml
    cur_dir = Path(__file__).absolute().parent
    cas_dir = cur_dir / "cassettes"
    module_name = ".".join(request.module.__name__.split(".")[1:])
    mod_dir = cas_dir / module_name
    return str(mod_dir)


def pytest_collection_modifyitems(config, items):
    global NEEDS_DOCKER

    for cur_item in items:
        #vcr_marker = "vcr" in [x.name for x in cur_item.own_markers]
        is_skip = "skip" in [x.name for x in cur_item.own_markers]
        if is_skip:
            continue

        # nodeid looks like tests/module/submodule.py::test_function
        # generate full path to the cassette which is of the form:
        #   tests/cassettes/<module_name>/<test_function>.yaml
        # for cases when there are multiple module folders containing tests
        # the subfolder for tests will be dot-separated folder name as in:
        #   module1.module2
        # example:
        #   tests/cassettes/module1.module2/test_function.yaml
        node_path = Path(cur_item.nodeid.split("::")[0].replace(".py", ""))
        sub_dir = ".".join(node_path.parts[1:])

        test_dir = Path(__file__).parent
        cassette_file = test_dir / "cassettes" / sub_dir / Path(f"{cur_item.name}.yaml")

        spec = inspect.getfullargspec(cur_item.obj)
        test_fixtures = ["test_builds_with_git", "test_builds", "test_job", "jenkins_api"]
        depends_on_jenkins = False
        for cur_fixture in test_fixtures:
            if cur_fixture in spec.args:
                depends_on_jenkins = True
                break

        if depends_on_jenkins and not cassette_file.exists():
            print(f"Launching Docker because of test {cur_item.name}")
            NEEDS_DOCKER = True
            return
    # If we see no other reason to use Docker from the logic above,
    # see if the caller has explicitly asked to use the container
    NEEDS_DOCKER = config.getoption("--regenerate")
