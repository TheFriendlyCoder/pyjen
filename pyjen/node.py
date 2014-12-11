"""Declarations for the abstraction of a Jenkins build agent"""
import time
import sys
if sys.version_info.major < 3:
    from urllib import quote as url_quote
else:
    from urllib.parse import quote as url_quote


class Node(object):
    """Wrapper around a Jenkins build agent (aka: Node) configuration

    Use this class to manipulate agents managed by a Jenkins master

    Instances of this class are typically created using one of the node
    methods on the Jenkins class, such as :py:meth:`~.jenkins.Jenkins.find_node`
    """

    def __init__(self, data_io_controller):
        """To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        """
        self._data_io = data_io_controller

    @property
    def name(self):
        """Gets the display name of this Node

        :returns: the name of this Node
        :rtype: :class:`str`
        """
        data = self._data_io.get_api_data()

        return data['displayName']

    @property
    def is_offline(self):
        """Checks to see whether this Node is currently offline or not

        :returns: True if this Node is offline otherwise False
        :rtype: :class:`bool`
        """
        data = self._data_io.get_api_data()

        return data['offline']

    @property
    def is_idle(self):
        """Checks to see whether any executors are in use on this Node or not

        :returns:
            returns True if there are no active builds on this Node at the
            moment otherwise returns False
        :rtype: :class:`bool`
        """
        data = self._data_io.get_api_data()
        return data['idle']
    
    def toggle_offline(self, message=None):
        """Toggles the online status of this Node

        If the current state of this Node is "offline" it will
        be toggled to "online" when calling this method, and vice
        versa.

        :param str message:
            optional descriptive message to display on the dashboard explaining
            the reason this node has been taken offline.
        """
        if message is not None:
            post_cmd = "/toggleOffline?offlineMessage=" + url_quote(message)
        else:
            post_cmd = "/toggleOffline"

        self._data_io.post(post_cmd)

    def wait_for_idle(self, max_timeout=None):
        """Blocks execution until this Node enters an idle state

        :param int max_timeout:
            The maximum amount of time, in seconds, to wait for
            an idle state. If this value is undefined, this method
            will block indefinitely.

        :returns:
            True if the Node has entered idle state before returning
            otherwise returns False
        :rtype: :class:`bool`
        """
        sleep_duration = 1

        if max_timeout is None:
            while not self.is_idle:
                time.sleep(sleep_duration)
        else:
            total_wait_time = 0
            while not self.is_idle:
                time.sleep(sleep_duration)
                total_wait_time += sleep_duration
                if total_wait_time >= max_timeout:
                    break

        return self.is_idle

if __name__ == "__main__":  # pragma: no cover
    pass
