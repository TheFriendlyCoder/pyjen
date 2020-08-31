"""Interfaces for managing plugins for a particular Jenkins instance"""
from pyjen.plugin import Plugin


class PluginManager:
    """Abstraction around Jenkins plugin management interfaces

    Supports adding, removing and querying information about Jenkins plugins
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
    def plugins(self):
        """list (Plugin): interfaces describing the plugins installed on the
        current Jenkins instance"""
        res = self._api.get_api_data(query_params='depth=2')

        retval = []

        for cur_plugin in res['plugins']:
            tmp_plugin = Plugin(cur_plugin)
            retval.append(tmp_plugin)
        return retval

    def find_plugin_by_shortname(self, short_name):
        """Finds an installed plugin based on it's abbreviated name

        Args:
            short_name (str):
                abbreviated form of the plugin name to locate

        Returns:
            Plugin:
                reference to the given plugin, or None if no plugin with the
                specified short name could be found
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

        Args:
            plugin_file (str):
                path to the HPI/JPI file to install
        """
        with open(plugin_file, 'rb') as handle:
            files = {'file': handle}
            self._api.post(self._api.url + 'uploadPlugin', {"files": files})


if __name__ == "__main__":  # pragma: no cover
    pass
