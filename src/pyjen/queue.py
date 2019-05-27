"""Abstration around the Jenkins build queue"""
from pyjen.queue_item import QueueItem


class Queue(object):
    """Abstraction around the Jenkins build queue

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(Queue, self).__init__()
        self._api = api

    @property
    def _data(self):
        """Gets the API data describing the current state of the build queue

        :rtype: :class:`dict`
        """
        retval = self._api.get_api_data()
        assert retval["_class"] == "hudson.model.Queue"
        return retval

    @property
    def items(self):
        """Gets a list of scheduled builds waiting in the queue

        :rtype: :class:`list` of :class:`QueueItem`
        """
        retval = list()
        for cur_item in self._data["items"]:
            queue_api = self._api.clone(self._api.root_url + cur_item["url"])
            retval.append(QueueItem(queue_api))
        return retval


if __name__ == "__main__":  # pragma: no cover
    pass
