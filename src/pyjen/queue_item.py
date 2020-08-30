"""Abstraction around a scheduled build contained in the Jenkins build queue"""
from urllib.parse import urlsplit
import requests
from requests.exceptions import HTTPError
from pyjen.build import Build
from pyjen.utils.plugin_api import find_plugin


class QueueItem:
    """Abstraction around a scheduled build contained in the Jenkins build queue
    """

    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api

    def __eq__(self, other):
        if not isinstance(other, QueueItem):
            return False
        return self._api.url == other._api.url  # pylint: disable=protected-access

    def __ne__(self, other):
        if not isinstance(other, QueueItem):
            return True
        return self._api.url != other._api.url  # pylint: disable=protected-access

    @property
    def _data(self):
        """dict: API data describing the current state of the queued build

        May return an empty dictionary if the object is no longer backed by a
        valid REST API endpoint.
        """
        try:
            return self._api.get_api_data()
        except HTTPError as err:
            if err.response.status_code == requests.codes.NOT_FOUND:
                return dict()
            raise

    @property
    def uid(self):
        """int: unique numeric identifier of this queued build

        Guaranteed to return a valid identifier, even when the queue item
        this object refers to has been invalidated by Jenkins.
        """
        # We could try and pull the item ID from the "id" field of our response
        # data, but to ensure we always have the ability to return a valid
        # ID even when this queue item has been cleaned up server-side, we
        # extrapolate the ID from the URL.
        #
        # Queue items are defined by a URL that look something like this:
        #       https://server/queue/item/1234
        parts = urlsplit(self._api.url).path.split("/")
        parts = [cur_part for cur_part in parts if cur_part.strip()]
        queue_id = parts[-1]
        assert queue_id.isnumeric()

        return int(queue_id)

    @property
    def stuck(self):
        """bool: Is this scheduled build blocked / unable to build?

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        return self._data.get("stuck")

    @property
    def blocked(self):
        """bool: Is this scheduled build waiting for some other event to
        complete?

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        return self._data.get("blocked")

    @property
    def buildable(self):
        """bool: is this queued build able to be built on this build farm?

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        return self._data.get("buildable")

    @property
    def reason(self):
        """str: Descriptive text explaining why this build is still in the queue

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        if not self._data.keys():
            return None
        return self._data.get("why", "")

    @property
    def waiting(self):
        """bool: Is this queue item still waiting in the queue?

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        temp = self._data.get("_class")
        if temp is None:
            return None
        return "$WaitingItem" in temp

    @property
    def cancelled(self):
        """bool: Has this queued build been cancelled?

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        if not self._data.keys():
            return None
        return self._data.get("cancelled", False)

    @property
    def job(self):
        """Job: the Jenkins job associated with this scheduled build

        Warning:
            May return None if this queue item has been invalidated by Jenkins
        """
        job_data = self._data.get("task")
        if job_data is None:
            return None
        plugin = find_plugin(job_data["_class"])
        if plugin is None:
            raise NotImplementedError(
                "Job plugin not supported: " + job_data["_class"])
        return plugin(self._api.clone(job_data["url"]))

    @property
    def build(self):
        """Build: Once this scheduled build leaves the queue, this property
        returns a reference to the running build. While the item is still
        queued, this property returns None.

        See the :py:meth:`.waiting` property on this object for a way to detect
        whether a queued item has left the queue or not.
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
            "params": {"id": self.uid},
        }
        self._api.post(tmp_url, params)

    def is_valid(self):
        """bool: Checks to make sure the queue item this object manages still
        exists

        Jenkins periodically expires / invalidates queue items server-side.
        There is no way for us to detect or predict when this will happen. When
        it does, this client-side queue item object will no longer refer to
        a valid REST API endpoint. This helper method helps users of the PyJen
        library check to see if the object still points to a valid queue item.
        """
        return bool(self._data.keys())


if __name__ == "__main__":  # pragma: no cover
    pass
