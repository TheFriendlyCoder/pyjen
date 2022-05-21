"""Abstraction around the Jenkins build queue"""
from pyjen.queue_item import QueueItem


class Queue:
    """Abstraction around the Jenkins build queue"""

    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api

    @property
    def _data(self):
        """dict: API data describing the current state of the build queue"""
        retval = self._api.get_api_data()
        assert retval["_class"] == "hudson.model.Queue"
        return retval

    @property
    def items(self):
        """list (QueueItem): list of scheduled builds waiting in the queue"""
        retval = []
        for cur_item in self._data["items"]:
            queue_api = self._api.clone(self._api.root_url + cur_item["url"])
            retval.append(QueueItem(queue_api))
        return retval


if __name__ == "__main__":  # pragma: no cover
    pass
