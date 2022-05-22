"""Primitives for manipulating Dockerized Jenkins test environment"""
import logging
import json
import io
import os
import tarfile
from pathlib import Path
from docker import APIClient
from docker.errors import DockerException


class JenkinsManager:
    """Management interface for interacting with Jenkins via Docker"""
    def __init__(self, image_name, plugin_names):
        """
        Args:
            image_name (str):
                Name of the Docker image to use for the test environment
            plugin_names (list of str):
                list of 0 or more Jenkins plugins to be deployed into the
                test environment
        """
        self._image_name = image_name
        self._plugin_names = plugin_names
        self._image_id = None
        self._container_id = None
        self._url = None
        self._auth_password = None
        self._auth_user = "admin"
        self._log = logging.getLogger(__name__)
        try:
            self._client = APIClient(version="auto")
        except DockerException as err:
            self._log.error("Unable to connect to Docker service. Make sure "
                            "you have Docker installed and that the service is "
                            "running.")
            self._log.exception(err)
            raise

    @property
    def _container_id_file(self):
        """pathlib.Path: file containing the Docker ID for the previously
        launched environment"""
        return Path(__file__).absolute().parent.parent / "container_id.txt"

    @property
    def _auth_token_file(self):
        """pathlib.Path: file containing the authentication token for the root
        user to authenticate with against the Jenkins REST API"""
        return Path(__file__).absolute().parent.parent / "container_id.txt.token"

    def _extract_file(self, path):
        """Extracts a single file from a Docker container

        Extraction is performed in-memory to improve performance and minimize
        disk dependency

        Args:
            path (str):
                path within the container where the file to extract

        Returns:
            str: contents of the specified file
        """
        # Get docker to generate an in memory tar ball for the file
        byte_stream, stats = self._client.get_archive(self._container_id, path)
        self._log.debug(json.dumps(stats, indent=4))

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

    def _inject_file(self, local_file_path, container_path):
        """Adds a single file to a Docker container

        Args:
            local_file_path (str):
                path to the local file to add to the container
            container_path (str):
                path within the container to inject the file to
        """
        # TODO: Test this method
        # TODO: rework to use pathlib
        # TODO: put temporary file in system temp folder
        if os.path.exists("temp.tar"):
            os.unlink("temp.tar")

        with tarfile.open("temp.tar", 'w') as tar:
            tar.add(local_file_path)

        with open("temp.tar") as tf:
            self._client.put_archive(self._container_id, container_path, tf)

        os.unlink("temp.tar")

    @property
    def container_id(self):
        """str: returns the Docker container ID of the running container.
        May be None if the test environment is not running."""
        return self._container_id

    @property
    def url(self):
        """str: URL to be used when communicating with the Jenkins service"""
        return self._url

    @property
    def user(self):
        """str: admin user to authenticate with against the Jenkins REST API"""
        return self._auth_user

    @property
    def password(self):
        """str: password for the authenticated Jenkins API user"""
        return self._auth_password

    def get_image(self):
        """
        Make sure we have a copy of the Docker image in the local cache.
        If we do already have a copy of the image locally, we don't need to pull
        a new copy. This allows us to run the tests offline so long as the
        local Docker cache contains the image we need
        """

        found_image = False
        for cur_image in self._client.images():
            if self._image_name in cur_image["RepoTags"]:
                found_image = True
                break
        if not found_image:
            self._log.info("Pulling Jenkins Docker image...")
            for cur_line in self._client.pull(
                    self._image_name, stream=True, decode=True):
                self._log.debug(json.dumps(cur_line, indent=4))

    def create_container(self):
        if self._container_id_file.exists():
            # TODO: See if the running container is using the same Jenkins
            #       version that has been requested for this run and start
            #       a new container if not
            temp_id = self._container_id_file.read_text("utf-8").strip()
            self._log.info(f"Reusing existing container {temp_id}")

            res = self._client.containers(filters={"id": temp_id})
            if res:
                self._container_id = temp_id
                res = self._client.inspect_container(temp_id)
                self._image_id = res["Image"]
                return

        # Generate a custom Dockerfile on the fly for our test environment
        dockerfile = f"FROM {self._image_name}\n"
        if self._plugin_names:
            dockerfile += f"RUN /usr/local/bin/install-plugins.sh {' '.join(self._plugin_names)}\n"

        # Build our Dockerfile and extract the SHA ID for the generated image
        # from the log output
        for cur_line in self._client.build(fileobj=io.BytesIO(dockerfile.encode('utf-8')), nocache=True, rm=True, decode=True):
            self._log.debug(cur_line)
            if "aux" in cur_line:
                self._image_id = cur_line["aux"]["ID"]
        assert self._image_id

        # Launch a container from the built Docker image
        hc = self._client.create_host_config(
            port_bindings={8080: None},
        )
        res = self._client.create_container(
            self._image_id, host_config=hc, volumes=["/var/jenkins_home"],
        )
        self._container_id = res["Id"]
        self._container_id_file.write_text(self._container_id, "utf-8")
        self._log.debug(f"Container {self._container_id} created")

    def launch_container(self):
        assert self._container_id
        self._client.start(self._container_id)

        # Look for a magic phrase in the log output from our container
        # to see when the Jenkins service is up and running before running
        # any tests
        self._log.info("Waiting for Jenkins Docker container to start...")
        magic_message = "Jenkins is fully up and running"

        # Parse admin password from container
        for cur_log in self._client.logs(self._container_id, stream=True, follow=True):
            temp = cur_log.decode("utf-8").strip()
            if magic_message in temp:
                break
        self._log.info("Container started. Extracting admin token...")
        self._auth_password = self._extract_file(
            "/var/jenkins_home/secrets/initialAdminPassword")
        self._auth_token_file.write_text(self._auth_password, "utf-8")
        self._log.info(f"Extracted token {self._auth_password}")

        # prepare connection parameters for the docker environment
        # for the tests to use
        http_port = self._client.port(self._container_id, 8080)[0]["HostPort"]
        self._url = f"http://localhost:{http_port}"

    def stop_container(self):
        """Terminates the test environment and cleans up temporary storage"""
        self._client.stop(self._container_id)

        self._client.remove_container(self._container_id, v=True, force=True)
        self._container_id = None

        self._client.remove_image(self._image_id)
        self._image_id = None

        self._container_id_file.unlink()
        self._auth_token_file.unlink()
