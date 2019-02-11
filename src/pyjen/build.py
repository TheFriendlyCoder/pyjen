"""Primitives for interacting with Jenkins builds"""
from datetime import datetime
import logging
from pyjen.changeset import Changeset
from pyjen.utils.jenkins_api import JenkinsAPI
from six.moves import urllib_parse


class Build(JenkinsAPI):
    """Class that encapsulates information about a single build / run of a :class:`~.job.Job`

    Builds are executions of jobs and thus instances of this class are
    typically generated from the :class:`~.job.Job` class.

    .. seealso:: :class:`~.job.Job`

    :param str url: Full URL of one particular build of a Jenkins job
    """

    def __init__(self, url):
        super(Build, self).__init__(url)
        self._log = logging.getLogger(__name__)

    def __eq__(self, obj):
        """Equality operator"""
        if not isinstance(obj, Build):
            return False

        if obj.id != self.id:
            return False

        if obj.number != self.number:
            return False

        return True

    def __ne__(self, obj):
        """Inequality operator"""
        if not isinstance(obj, Build):
            return True

        if obj.id != self.id:
            return True

        if obj.number != self.number:
            return True

        return False

    def __hash__(self):
        """Hashing function, allowing object to be serialized and compared"""
        return hash(self.id)

    @property
    def number(self):
        """Gets the sequence number of this build

        :returns: sequentially assigned integer value associated with this build
        :rtype: :class:`int`
        """

        data = self.get_api_data()

        return data['number']

    @property
    def start_time(self):
        """Gets the time stamp of when this build was started

        :returns: the date and time at which this build was started
        :rtype: :class:`datetime.datetime`

        """

        data = self.get_api_data()

        time_in_seconds = data['timestamp'] * 0.001

        return datetime.fromtimestamp(time_in_seconds)

    @property
    def is_building(self):
        """Checks to see whether this build is currently executing

        :returns: True if the build is executing otherwise False
        :rtype: :class:`bool`
        """
        data = self.get_api_data()

        return data['building']

    @property
    def console_output(self):
        """Gets the raw console output for this build as plain text

        :returns: Raw console output from this build, in plain text format
        :rtype: :class:`str`
        """
        return self.get_text("/consoleText")

    @property
    def result(self):
        """Gets the status of the build

        :returns:
            Result state of the associated job upon completion of this build. Typically one of the following:

            * "SUCCESS"
            * "UNSTABLE"
            * "FAILED"
        :rtype: :class:`str`
        """
        data = self.get_api_data()

        return data['result']

    @property
    def changeset(self):
        """Gets the list of SCM changes associated with this build

        :returns: 0 or more SCM changesets associated with / included in this build.
        :rtype: :class:`~.changeset.Changeset`
        """
        data = self.get_api_data()

        return Changeset(data['changeSet'])

    @property
    def description(self):
        """Gets the descriptive text associated with this build. May be an empty string if no description given.

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        retval = data["description"]
        if retval is None:
            return ""
        return retval

    @property
    def id(self):  # pylint: disable=invalid-name
        """Gets the unique identifier associated with this build

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        return data["id"]

    @property
    def artifact_urls(self):
        """Gets a list of 0 or more URLs which can be used to download the published build artifacts for this build

        :rtype: :class:`list` of :class:`str`
        """
        data = self.get_api_data()
        artifacts_node = data['artifacts']
        retval = []

        for node in artifacts_node:
            url = urllib_parse.urljoin(self.url, "artifact/" + node['fileName'])
            retval.append(url)

        return retval


if __name__ == "__main__":  # pragma: no cover
    pass
