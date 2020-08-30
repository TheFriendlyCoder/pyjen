"""Primitives for interacting with Jenkins builds"""
from datetime import datetime
import logging
from urllib.parse import urljoin
from pyjen.changeset import Changeset


class Build:
    """information about a single build / run of a :class:`~.job.Job`"""

    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api
        self._log = logging.getLogger(__name__)

    def __eq__(self, obj):
        if not isinstance(obj, Build):
            return False

        if obj.uid != self.uid:
            return False

        return True

    def __ne__(self, obj):
        if not isinstance(obj, Build):
            return True

        if obj.uid != self.uid:
            return True

        return False

    def __hash__(self):
        return hash(self.uid)

    @property
    def url(self):
        """str: URL of this build"""
        return self._api.url

    @property
    def number(self):
        """int: sequentially assigned numeric ID for the build"""

        data = self._api.get_api_data()

        return data['number']

    @property
    def start_time(self):
        """datetime.datetime: time stamp of when this build was started"""

        data = self._api.get_api_data()

        time_in_seconds = data['timestamp'] * 0.001

        return datetime.fromtimestamp(time_in_seconds)

    @property
    def is_building(self):
        """bool: True if the build is currently executing otherwise False"""
        data = self._api.get_api_data()
        return data['building']

    @property
    def console_output(self):
        """str: raw console output for this build as plain text"""
        return self._api.get_text("/consoleText")

    @property
    def result(self):
        """str: state of the associated job upon completion of this build.
        Typically one of the following:

            * "SUCCESS"
            * "UNSTABLE"
            * "FAILURE"
            * "ABORTED"
        """
        data = self._api.get_api_data()
        return data['result']

    @property
    def changeset(self):
        """Changeset: Description of 0 or more SCM revisions associated with
        / included in this build"""
        data = self._api.get_api_data()

        return Changeset(self._api, data['changeSet'])

    @property
    def description(self):
        """str: Gets the descriptive text associated with this build. May be an
        empty string if no description given."""
        data = self._api.get_api_data()
        retval = data["description"]
        if retval is None:
            return ""
        return retval

    @description.setter
    def description(self, value):
        args = {
            'params': {
                'description': value,
                'Submit': "Submit"
            }
        }
        self._api.post(self.url + '/submitDescription', args=args)

    @property
    def uid(self):
        """str: internal, unique identifier associated with this build"""
        data = self._api.get_api_data()
        return data["id"]

    @property
    def artifact_urls(self):
        """list (): list of 0 or more URLs to download published build artifacts
        """
        data = self._api.get_api_data()
        artifacts_node = data['artifacts']
        retval = []

        for node in artifacts_node:
            url = urljoin(
                self._api.url, "artifact/" + node['fileName'])
            retval.append(url)

        return retval

    @property
    def duration(self):
        """int: total runtime of the build, in milliseconds. Returns 0 if
        build hasn't finished"""
        data = self._api.get_api_data()
        return data['duration']

    @property
    def estimated_duration(self):
        """int: Estimated runtime for a running build, in milliseconds.
        Estimate is based off average duration of previous builds"""
        data = self._api.get_api_data()
        return data['estimatedDuration']

    def abort(self):
        """Aborts this build before it completes"""
        self._api.post(self._api.url + "stop")

    def kill(self):
        """Performs hard kill on this build"""
        self._api.post(self._api.url + "kill")


if __name__ == "__main__":  # pragma: no cover
    pass
