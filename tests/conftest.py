import os
import shutil
import tarfile
import io
import json
import pytest
import logging
import docker
from docker.errors import DockerException

# TODO: Add support for Jenkins 1 testing

# Global flag used to see whether we've already attempted to run our Jenkins
# containerized environment. Prevents redundant failures from slowing down
# the test runner
FAILED_DOCKER_SETUP = False


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
        default="jenkins:alpine",
        help="Name of docker container for the Jenkins version to test against"
    )


def extract_file(client, container, path):
    """Extracts a single file from a Docker container

    Extraction is performed in-memory to improve performance and minimize
    disk dependency

    :param client: Docker API connection to the service
    :param int container: ID of the container to work with
    :param str path:
        path within the container where the file to extract
    :returns: contents of the specified file
    :rtype: :class:`str`
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


def _workspace_dir():
    """Gets the absolute path to the root folder of the workspace

    :rtype: :class:`str`
    """
    cur_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(cur_path, ".."))


@pytest.fixture(scope="session", autouse=True)
def configure_logger():
    """Configure logging for the test runner"""
    log_dir = os.path.join(_workspace_dir(), "logs")
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    global_log = logging.getLogger()
    global_log.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(
        os.path.join(log_dir, "tests.log"),
        mode="w")
    file_handler.setLevel(logging.DEBUG)
    global_log.addHandler(file_handler)


@pytest.fixture(scope="session")
def jenkins_env(request, configure_logger):
    """Fixture that generates a dockerized Jenkins environment for testing"""
    global FAILED_DOCKER_SETUP
    log = logging.getLogger(__name__)

    if FAILED_DOCKER_SETUP:
        raise Exception(
            "Skipping Docker setup logic. Previous attempt failed.")

    image_name = request.config.getoption("--jenkins-version")
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

    if os.path.exists(container_id_file):
        with open(container_id_file) as file_handle:
            container_id = file_handle.read().strip()
        log.info("Reusing existing container %s", container_id)
    else:
        res = client.create_container(
            image_name, host_config=hc, volumes=["/var/jenkins_home"])
        log.debug(json.dumps(res, indent=4))
        container_id = res["Id"]
        log.debug("Container %s created", container_id)

    if preserve_container:
        with open(container_id_file, mode="w") as file_handle:
            file_handle.write(container_id)

    try:
        log.info("Starting Jenkins Docker container...")
        client.start(container_id)
        # Look for a magic phrase in the log output from our container
        # to see when the Jenkins service is up and running before running
        # any tests
        log.info("Waiting for Jenkins Docker container to start...")
        magic_message = "Jenkins is fully up and running"
        for cur_log in client.logs(container_id, stream=True, follow=True):
            temp = cur_log.decode("utf-8").strip()
            if magic_message in temp:
                break

        # Parse admin password from container
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
        }
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


def pytest_collection_modifyitems(config, items):
    """Applies command line customizations to filter tests to be run"""
    if not config.getoption("--skip-docker"):
        return

    skip_jenkins = pytest.mark.skip(reason="Skipping Jenkins Server tests")
    for item in items:
        if "jenkins_env" in item.fixturenames:
            item.add_marker(skip_jenkins)