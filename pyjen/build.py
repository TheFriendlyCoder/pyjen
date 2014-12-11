"""Primitives for interacting with Jenkins builds"""

from pyjen.changeset import Changeset
from datetime import datetime


class Build(object):
    """Class that encapsulates information about a single build / run of a :class:`~.job.Job`

    Builds are executions of jobs and thus instances of this class are
    typically generated from the :class:`~.job.Job` class.

    .. seealso:: :class:`~.job.Job`
    """

    def __init__(self, data_io_controller):
        """
        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        """
        self._data_io = data_io_controller
    
    def __eq__(self, obj):
        """Overrides the default equality operation"""
        if isinstance(obj, Build):
            data = self._data_io.get_api_data()
            build_url = data['url']
            obj_data = obj._data_io.get_api_data()
            obj_build_url = obj_data["url"]
            return build_url == obj_build_url
        raise RuntimeError("Objects do not match")
    
    def __ne__(self, obj):
        """Overrides the default not equal operation"""
        if isinstance(obj, Build):
            data = self._data_io.get_api_data()
            build_url = data['url']
            obj_data = obj._data_io.get_api_data()
            obj_build_url = obj_data["url"]
            return build_url != obj_build_url
        raise RuntimeError("Objects do not match")
        
    @property
    def build_number(self):
        """Gets the numeric build number for this build

        :returns: This is the unique numeric identifier, typically a sequential integer that is incremented
            with each build.
        :rtype: :class:`int`
        """

        data = self._data_io.get_api_data()

        return data['number']    
    

    @property
    def build_time(self):
        """Gets the time stamp of when this build was executed

        :returns: the date and time at which this build was executed
        :rtype: :class:`datetime.datetime`

        """

        data = self._data_io.get_api_data()

        time_in_seconds = data['timestamp'] * 0.001

        return datetime.fromtimestamp(time_in_seconds)

    @property
    def is_building(self):
        """Checks to see whether this build is currently executing

        :returns: True if the build is executing otherwise False
        :rtype: :class:`bool`
        """
        data = self._data_io.get_api_data()

        return data['building']

    @property
    def console_output(self):
        """Gets the raw console output for this build as plain text

        :returns: Raw console output from this build, in plain text format
        :rtype: :class:`str`
        """
        return self._data_io.get_text("/consoleText")

    @property
    def changeset(self):
        """Gets the list of SCM changes associated with this build

        :returns: 0 or more SCM changesets associated with / included in this build.
            If no changesets are found, returns None
        :rtype: :class:`~.changeset.Changeset`
        """
        data = self._data_io.get_api_data()

        return Changeset(data['changeSet'], self._data_io)


if __name__ == "__main__":  # pragma: no cover
    pass
