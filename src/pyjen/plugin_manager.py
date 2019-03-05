"""Interfaces for managing plugins for a particular Jenkins instance"""
from pyjen.plugin import Plugin


class PluginManager(object):
    """Abstraction around Jenkins plugin management interfaces

    Supports adding, removing and querying information about Jenkins plugins

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(PluginManager, self).__init__()
        self._api = api

    @property
    def plugins(self):
        """list of all installed plugins from the current Jenkins instance

        :returns: list of 0 or more plugins installed on the Jenkins instance
        :rtype: List of 0 or more :class:`~.plugin.Plugin` objects"""
        res = self._api.get_api_data(query_params='depth=2')

        retval = []

        for cur_plugin in res['plugins']:
            tmp_plugin = Plugin(cur_plugin)
            retval.append(tmp_plugin)
        return retval

    def find_plugin_by_shortname(self, short_name):
        """Finds an installed plugin based on it's abbreviated name

        :param str short_name:
            abbreviated form of the plugin name to locate

        :returns:
            reference to the given plugin, or None if no such plugin found
        :rtype: :class:`~.plugin.Plugin`
        """
        for cur_plugin in self.plugins:
            if cur_plugin.short_name == short_name:
                return cur_plugin
        return None

    def install_plugin(self, plugin_file):
        """Installs a new plugin on the selected Jenkins instance

        NOTE: If using this method to batch-install many plugins at once you
        may want to add a short wait / sleep between calls so as to not
        overwhelm the target server with upload requests. Ad-hoc tests show
        that Jenkins will refuse connections if too many uploads are running
        in parallel.

        :param str plugin_file: path to the HPI/JPI file to install
        """
        with open(plugin_file, 'rb') as handle:
            files = {'file': handle}
            self._api.post(self._api.url + 'uploadPlugin', {"files": files})


if __name__ == "__main__":  # pragma: no cover
    pass
