"""Primitives for interacting with Jenkins builds"""
from datetime import datetime
import logging
from six.moves import urllib_parse
from pyjen.changeset import Changeset


class Build(object):
    """information about a single build / run of a :class:`~.job.Job`

    Builds are executions of jobs and thus instances of this class are
    typically generated from the :class:`~.job.Job` class.

    .. seealso:: :class:`~.job.Job`

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(Build, self).__init__()
        self._api = api
        self._log = logging.getLogger(__name__)

    def __eq__(self, obj):
        """Equality operator"""
        if not isinstance(obj, Build):
            return False

        if obj.uid != self.uid:
            return False

        return True

    def __ne__(self, obj):
        """Inequality operator"""
        if not isinstance(obj, Build):
            return True

        if obj.uid != self.uid:
            return True

        return False

    def __hash__(self):
        """Hashing function, allowing object to be serialized and compared"""
        return hash(self.uid)

    @property
    def url(self):
        """Gets the URL of this build

        :returns: full url to this build
        :rtype: :class:`str`
        """
        return self._api.url

    @property
    def number(self):
        """Gets the sequence number of this build

        :returns: sequentially assigned integer value associated with this build
        :rtype: :class:`int`
        """

        data = self._api.get_api_data()

        return data['number']

    @property
    def start_time(self):
        """Gets the time stamp of when this build was started

        :returns: the date and time at which this build was started
        :rtype: :class:`datetime.datetime`

        """

        data = self._api.get_api_data()

        time_in_seconds = data['timestamp'] * 0.001

        return datetime.fromtimestamp(time_in_seconds)

    @property
    def is_building(self):
        """Checks to see whether this build is currently executing

        :returns: True if the build is executing otherwise False
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()
        return data['building']

    @property
    def console_output(self):
        """Gets the raw console output for this build as plain text

        :returns: Raw console output from this build, in plain text format
        :rtype: :class:`str`
        """
        return self._api.get_text("/consoleText")

    @property
    def result(self):
        """Gets the status of the build

        :returns:
            Result state of the associated job upon completion of this build.
            Typically one of the following:

            * "SUCCESS"
            * "UNSTABLE"
            * "FAILURE"
            * "ABORTED"

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['result']

    @property
    def changeset(self):
        """Gets the list of SCM changes associated with this build

        :returns:
            0 or more SCM changesets associated with / included in this build.
        :rtype: :class:`~.changeset.Changeset`
        """
        data = self._api.get_api_data()

        return Changeset(self._api, data['changeSet'])

    @property
    def description(self):
        """Gets the descriptive text associated with this build.

        May be an empty string if no description given.

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        retval = data["description"]
        if retval is None:
            return ""
        return retval

    @property
    def uid(self):
        """Gets the unique identifier associated with this build

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data["id"]

    @property
    def artifact_urls(self):
        """list of 0 or more URLs to download published build artifacts

        :rtype: :class:`list` of :class:`str`
        """
        data = self._api.get_api_data()
        artifacts_node = data['artifacts']
        retval = []

        for node in artifacts_node:
            url = urllib_parse.urljoin(
                self._api.url, "artifact/" + node['fileName'])
            retval.append(url)

        return retval

    @property
    def duration(self):
        """Total runtime of the build, in milliseconds

        Returns 0 if build hasn't finished

        :rtype: :class:`int`
        """
        data = self._api.get_api_data()
        return data['duration']

    @property
    def estimated_duration(self):
        """Estimated runtime for a running build

        Estimate is based off average duration of previous builds,
        in milliseconds

        :rtype: :class:`int`
        """
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
