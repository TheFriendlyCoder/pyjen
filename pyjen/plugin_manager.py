"""Interfaces for managing plugins for a particular Jenkins instance"""
from pyjen.plugin import Plugin


class PluginManager(object):
    """Abstraction around Jenkins plugin management interfaces

    Supports adding, removing and querying information about Jenkins plugins"""

    def __init__(self, data_io_controller):
        """Constructor
        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        """
        self._data_io = data_io_controller

    @property
    def plugins(self):
        """Gets a list of all installed plugins from the current Jenkins instance

        :returns: list of 0 or more plugins installed on the Jenkins instance
        :rtype: List of 0 or more :class:`~.plugin.Plugin` objects"""
        res = self._data_io.get_api_data('depth=2')

        retval = []

        for cur_plugin in res['plugins']:
            tmp_plugin = Plugin(cur_plugin)
            retval.append(tmp_plugin)

        return retval

    def install_plugin(self, plugin_file):
        """Installs a new plugin on the selected Jenkins instance

        NOTE: If using this method to batch-install many plugins at once you may want to add
        a short wait / sleep between calls so as to not overwhelm the target server with
        upload requests. Ad-hoc tests show that Jenkins will refuse connections if too many
        uploads are running in parallel.

        :param str plugin_file: path to the HPI/JPI file to install
        """
        with open(plugin_file, 'rb') as handle:
            files = {'file': handle}
            self._data_io.post('/uploadPlugin', files=files)

if __name__ == "__main__":
    pass
