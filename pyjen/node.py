"""Declarations for the abstraction of a Jenkins build agent"""

import time
import sys
if sys.version_info.major < 3:
    from urllib import quote as url_quote
else:
    from urllib.parse import quote as url_quote

from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError

class Node(object):
    """Wrapper around a Jenkins build agent (aka: Node) configuration

    Use this class to manipulate agents managed by a Jenkins master"""

    def __init__ (self, data_io_controller):
        """constructor

        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        """
        self.__data_io = data_io_controller

    @staticmethod
    def easy_connect(url, credentials=None):
        """Factory method to simplify creating connections to Jenkins servers

        :param str url: Full URL of the Jenkins instance to connect to.
            Must be a valid running Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and
            password for authenticating to the URL. If omitted, anonymous
            access will be chosen
        :returns: :py:mod:`pyjen.Node` object, pre-configured with the
            appropriate credentials and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.Node`
        """
        if credentials != None:
            username = credentials[0]
            password = credentials[1]
        else:
            username = ""
            password = ""

        http_io = data_requester(url, username, password)
        retval = Node(http_io)

        # Sanity check: make sure the given IO object can successfully
        #        query the Node machine name
        try:
            name = retval.get_name()
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters \
                provided to PyJen.Node. Please check configuration.", http_io)

        if name == None or name == "":
            raise InvalidJenkinsURLError("Invalid connection parameters \
                provided to PyJen.Node. Please check configuration.", http_io)
        return retval

    def get_name(self):
        """Gets the display name of this Node

        :returns: the name of this Node
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()

        return data['displayName']

    def is_offline(self):
        """Checks to see whether this Node is currently offline or not

        :returns: true if this Node is offline otherwise false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()

        return data['offline']

    def toggle_offline(self, message=None):
        """Toggles the online status of this Node

        If the current state of this Node is "offline" it will
        be toggled to "online" when calling this method, and vice
        versa.

        :param str message:
            optional descriptive message to display on the dashboard explaining
            the reason for this operation.
        """
        #todo: see if i can rework this to use args properties
        if message != None:
            post_cmd = "/toggleOffline?offlineMessage=" + url_quote(message)
        else:
            post_cmd = "/toggleOffline"

        self.__data_io.post(post_cmd)

    def is_idle(self):
        """Checks to see whether any executors are in use on this Node or not

        :returns:
            returns true if there are no active builds on this Node at the
            moment otherwise returns false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()
        return data['idle']

    def wait_for_idle(self, max_timeout=None):
        """Blocks execution until this Node enters an idle state

        :param int max_timeout:
            The maximum amount of time, in seconds, to wait for
            an idle state. If this value is undefined, this method
            will block indefinitely.

        :returns:
            true if the Node has entered idle state before returning
            otherwise returns false
        :rtype: :func:`bool`
        """
        sleep_duration = 1

        if max_timeout == None:
            while not self.is_idle():
                time.sleep(sleep_duration)
        else:
            total_wait_time = 0
            while not self.is_idle():
                time.sleep(sleep_duration)
                total_wait_time += sleep_duration
                if total_wait_time >= max_timeout:
                    break

        return self.is_idle()

if __name__ == "__main__":
    pass
