import os
import shutil
import tarfile
import io
import json
import pytest
import logging
import warnings
import docker
import multiprocessing
from docker.errors import DockerException
from pyjen.jenkins import Jenkins
from pyjen.plugins.freestylejob import FreestyleJob
from pyjen.plugins.gitscm import GitSCM
from .utils import async_assert


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
        "--jenkins-version",
        action="store",
        default=DEFAULT_JENKINS_VERSION,
        help="Name of docker container for the Jenkins version to test against"
    )


def extract_file(client, container, path):
    """Extracts a single file from a Docker container

    Extraction is performed in-memory to improve performance and minimize
    disk dependency

    Args:
        client:
            Docker API connection to the service
        container (int):
            ID of the container to work with
        path (str):
            path within the container where the file to extract

    Returns:
        str: contents of the specified file
    """
    log = logging.getLogger(__name__)

    # Get docker to generate an in memory tar ball for the file
    byte_stream, stats = client.get_archive(container, path)
    log.debug(json.dumps(stats, indent=4))

    # convert the in memory byte stream from a generator
    # to a file-like container
    in_memory_tar = io.BytesIO()
    for packet in byte_stream:
        in_memory_tar.write(packet)
    in_memory_tar.seek(0)

    # parse the in-memory tar data
    with tarfile.open(fileobj=in_memory_tar) as tf:
        cur_mem = tf.getmember(os.path.split(path)[1])
        return tf.extractfile(cur_mem).read().decode("utf-8").strip()


def inject_file(client, container, local_file_path, container_path):
    """Adds a single file to a Docker container

    Args:
        client:
            Docker API connection to the service
        container (int):
            ID of the container to work with
        local_file_path (str):
            path to the local file to add to the container
        container_path (str):
            path within the container to inject the file to
    """
    if os.path.exists("temp.tar"):
        os.unlink("temp.tar")

    with tarfile.open("temp.tar", 'w') as tar:
        tar.add(local_file_path)

    with open("temp.tar") as tf:
        client.put_archive(container, container_path, tf)

    os.unlink("temp.tar")


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

    image_name = request.config.getoption("--jenkins-version")
    log.info("Using Jenkins docker container '{0}'".format(image_name))
    preserve_container = request.config.getoption("--preserve")
    container_id_file = os.path.join(_workspace_dir(), "container_id.txt")

    try:
       client = docker.APIClient(version="auto")
    except DockerException as err:
        log.error("Unable to connect to Docker service. Make sure you have "
                  "Docker installed and that the service is running.")
        log.exception(err)
        FAILED_DOCKER_SETUP = True
        return

    # Make sure we have a copy of the Docker image in the local cache.
    # If we do already have a copy of the image locally, we don't need to pull
    # a new copy. This allows us to run the tests offline so long as the
    # local Docker cache contains the image we need
    found_image = False
    for cur_image in client.images():
        if image_name in cur_image["RepoTags"]:
            found_image = True
            break
    if not found_image:
        log.info("Pulling Jenkins Docker image...")
        for cur_line in client.pull(image_name, stream=True, decode=True):
            log.debug(json.dumps(cur_line, indent=4))

    # create our docker container, if one doesn't already exist
    log.info("Creating Jenkins Docker container...")
    hc = client.create_host_config(
        port_bindings={8080: None},
    )

    # First lets see if we can find a valid container already running
    container_id = None
    if os.path.exists(container_id_file):
        # TODO: See if the running container is using the same Jenkins
        #       version that has been requested for this run and start
        #       a new container if not
        with open(container_id_file) as file_handle:
            container_id = file_handle.read().strip()
        log.info("Reusing existing container %s", container_id)

        res = client.containers(filters={"id": container_id})
        if not res:
            container_id = None

    # if we can't find a container to use for the tests, create a new one
    if not container_id:
        # Generate a custom Dockerfile on the fly for our test environment
        dockerfile = "FROM {}\n".format(image_name)
        if JENKINS_PLUGINS:
            dockerfile += "RUN /usr/local/bin/install-plugins.sh {}\n".format(
                " ".join(JENKINS_PLUGINS)
            )

        # Build our Dockerfile and extract the SHA ID for the generated image
        # from the log output
        image_id = None
        for cur_line in client.build(fileobj=io.BytesIO(dockerfile.encode('utf-8')), rm=True, decode=True):
            log.debug(cur_line)
            if "aux" in cur_line:
                image_id = cur_line["aux"]["ID"]
        assert image_id

        # Launch a container from the built Docker image
        res = client.create_container(
            image_id, host_config=hc, volumes=["/var/jenkins_home"],
        )
        container_id = res["Id"]
        log.debug("Container %s created", container_id)

    try:
        # Setup background thread for redirecting log output to Python logger
        d = multiprocessing.Process(
            name='docker_logger',
            target=docker_logger,
            args=[container_id]
        )
        d.daemon = True
        d.start()

        log.info("Starting Jenkins Docker container...")
        client.start(container_id)

        # Look for a magic phrase in the log output from our container
        # to see when the Jenkins service is up and running before running
        # any tests
        log.info("Waiting for Jenkins Docker container to start...")
        magic_message = "Jenkins is fully up and running"

        # Parse admin password from container
        for cur_log in client.logs(container_id, stream=True, follow=True):
            temp = cur_log.decode("utf-8").strip()
            if magic_message in temp:
                break
        log.info("Container started. Extracting admin token...")
        token = extract_file(
            client,
            container_id,
            "/var/jenkins_home/secrets/initialAdminPassword")
        log.info("Extracted token " + str(token))

        # prepare connection parameters for the docker environment
        # for the tests to use
        http_port = client.port(container_id, 8080)[0]["HostPort"]
        data = {
            "url": "http://localhost:{0}".format(http_port),
            "admin_user": "admin",
            "admin_token": token,
            "plugins": JENKINS_PLUGINS[:],
        }

        # If the docker container launches successful, save the ID so we
        # can reuse the same container for the next test run
        if preserve_container:
            with open(container_id_file, mode="w") as file_handle:
                file_handle.write(container_id)
            with open(container_id_file + ".token", mode="w") as file_handle:
                file_handle.write(token)

        yield data
    finally:
        if preserve_container:
            log.info("Leaving Jenkins Docker container running: %s",
                     container_id)
            log.info("Container will be reused on next test run. To start "
                     "a new container on next run, delete this file: %s",
                     container_id_file)
        else:
            log.info("Shutting down Jenkins Docker container...")
            client.stop(container_id)
            client.remove_container(container_id)
            if os.path.exists(container_id_file):
                os.unlink(container_id_file)
            log.info("Done Docker cleanup")


@pytest.fixture(scope="function")
def jenkins_api(jenkins_env):
    """Test fixture that creates a connection to the Jenkins test server

    The API connection will use a basic-auth protocol using the connection
    parameters provided by the jenkins_env test fixture
    """
    jk = Jenkins.basic_auth(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))

    yield jk


@pytest.fixture(scope="class")
def test_job(request, jenkins_env):
    """Test fixture that creates a Jenkins Freestyle job for testing purposes

    The generated job is automatically cleaned up at the end of the test
    suite, which is defined as all of the methods contained within the same
    class.

    The expectation here is that tests that share this generated job will
    only perform read operations on the job and will not change it's state.
    This will ensure the tests within the suite don't affect one another.
    """
    jk = Jenkins.basic_auth(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    request.cls.jenkins = jk
    request.cls.job = jk.create_job(request.cls.__name__ + "Job", FreestyleJob)
    assert request.cls.job is not None

    yield

    request.cls.job.delete()


@pytest.fixture(scope="class")
def test_builds(request, test_job):
    """Helper fixture that creates a job with a sample good build for testing"""
    request.cls.job.quiet_period = 0
    request.cls.job.start_build()

    async_assert(lambda: request.cls.job.last_good_build)


@pytest.fixture(scope="class")
def test_builds_with_git(request, test_job):
    """Helper fixture that creates a job with a sample build with Git sources for testing"""
    expected_url = "https://github.com/TheFriendlyCoder/pyjen.git"
    test_scm = GitSCM.instantiate(expected_url)
    request.cls.job.scm = test_scm

    request.cls.job.quiet_period = 0
    async_assert(lambda: isinstance(request.cls.job.scm, GitSCM))

    request.cls.job.start_build()
    async_assert(lambda: request.cls.job.last_good_build is not None)


def pytest_collection_modifyitems(config, items):
    """Applies command line customizations to filter tests to be run"""
    if not config.getoption("--skip-docker"):
        return

    skip_jenkins = pytest.mark.skip(reason="Skipping Jenkins Server tests")
    for item in items:
        if "jenkins_env" in item.fixturenames:
            item.add_marker(skip_jenkins)
