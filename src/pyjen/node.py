"""Declarations for the abstraction of a Jenkins build agent"""
import time
from urllib.parse import quote


class Node:
    """Wrapper around a Jenkins build agent (aka: Node) configuration

    See :py:meth:`~.jenkins.Jenkins.find_node` for more details
    """

    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api

    @property
    def name(self):
        """str: the display name of this Node"""
        data = self._api.get_api_data()

        return data['displayName']

    @property
    def is_offline(self):
        """bool: checks to see whether this Node is currently offline or not"""
        data = self._api.get_api_data()

        return data['offline']

    @property
    def is_idle(self):
        """bool: checks to see whether any executors are in use on this Node
        or not"""
        data = self._api.get_api_data()
        return data['idle']

    @property
    def number_of_executors(self):
        """int: the number of executors this node provides"""
        data = self._api.get_api_data()
        return data['numExecutors']

    def toggle_offline(self, message=None):
        """Toggles the online status of this Node

        If the current state of this Node is "offline" it will be toggled to
        "online" and vice-versa.

        Args:
            message (str):
                optional descriptive message explaining the reason this node has
                been taken offline.
        """
        post_cmd = self._api.url + "toggleOffline"
        if message is not None:
            post_cmd += "?offlineMessage=" + quote(message)

        self._api.post(post_cmd)

    def wait_for_idle(self, max_timeout=None):
        """Blocks execution until this Node enters an idle state

        Args:
            max_timeout (int):
                Optional amount of time, in seconds, to wait for an idle
                state. If this value is undefined, this method will block
                indefinitely.

        Returns:
            bool:
                True if the Node has entered idle state before returning
                otherwise returns False
        """
        polling_period_in_seconds = 1

        total_wait_time = 0
        while not self.is_idle:
            time.sleep(polling_period_in_seconds)
            if max_timeout is None:
                continue

            total_wait_time += polling_period_in_seconds
            if total_wait_time >= max_timeout:
                break

        return self.is_idle


if __name__ == "__main__":  # pragma: no cover
    pass
