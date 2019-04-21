from pyjen.build import Build
from pyjen.utils.plugin_api import find_plugin
from pyjen.exceptions import PluginNotSupportedError


class QueueItem(object):
    """Abstraction around the Jenkins build queue

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(QueueItem, self).__init__()
        self._api = api

    def __eq__(self, other):
        if not isinstance(other, QueueItem):
            return False
        return self._api.url == other._api.url

    def __ne__(self, other):
        if not isinstance(other, QueueItem):
            return True
        return self._api.url != other._api.url

    @property
    def _data(self):
        """Gets the API data describing the current state of the queued build

        :rtype: :class:`dict`
        """
        retval = self._api.get_api_data()
        return retval

    @property
    def id(self):
        """Gets the numeric identifier of this queued build

        :rtype: :class:`int`
        """
        return int(self._data["id"])

    @property
    def stuck(self):
        """Is this scheduled build blocked / unable to build?

        :rtype: :class:`bool`
        """
        return self._data["stuck"]

    @property
    def blocked(self):
        """Is this scheduled build waiting for some other event to complete?

        :rtype: :class:`bool`
        """
        return self._data["blocked"]

    @property
    def buildable(self):
        """TBD

        :rtype: :class:`bool`
        """
        return self._data["buildable"]

    @property
    def reason(self):
        """Descriptive text explaining why this build is still in the queue

        :rtype: :class:`str`
        """
        return self._data["why"] or ""

    @property
    def waiting(self):
        """Is this queue item still waiting in the queue?

        :rtype: :class:`bool`
        """
        return "$WaitingItem" in self._data["_class"]

    @property
    def cancelled(self):
        """Has this queued build been cancelled?

        :rtype: :class:`bool`
        """
        return self._data["cancelled"]

    @property
    def job(self):
        """Gets the Jenkins job associated with this scheduled build

        :rtype: :class:`pyjen.job.Job`
        """
        job_data = self._data["task"]
        plugin = find_plugin(job_data["_class"])
        if plugin is None:
            raise PluginNotSupportedError(
                "Job plugin not supported.", job_data["_class"])
        return plugin(self._api.clone(job_data["url"]))

    @property
    def build(self):
        """Once this scheduled build leaves the queue, this property returns
        a reference to the running build. While the item is still queued, this
        property returns None.

        See the 'waiting' property on this object for a way to detect whether
        a queued item has left the queue or not.
        """
        exe_info = self._data.get("executable")
        if exe_info is None:
            return None
        return Build(self._api.clone(exe_info["url"]))

    def cancel(self):
        """Cancels this queued build"""
        tmp_url = self._api.root_url + "queue/cancelItem"
        params = {
            # Have to send a referrer in the header to circumvent this bug:
            # https://issues.jenkins-ci.org/browse/JENKINS-21311
            "headers": {'Referer': self._api.root_url},
            "params": {"id": self.id},
        }
        self._api.post(tmp_url, params)


if __name__ == "__main__":  # pragma: no cover
    pass
