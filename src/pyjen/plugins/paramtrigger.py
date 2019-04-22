"""Jenkins post-build publisher of type Parameterized Build Trigger"""
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import find_plugin


class ParameterizedBuildTrigger(XMLPlugin):
    """SCM plugin for Jobs with no source control configurations"""

    @property
    def triggers(self):
        """list of trigger operations defined for this instance of the plugin

        :rtype: :class:`list` of :class:`BuildTriggerConfig` objects
        """
        retval = list()
        configs_node = self._root.find('configs')
        for config in configs_node:
            plugin = find_plugin(config.tag)
            if plugin is None:
                self._log.warning("Skipping unsupported plugin: %s", config.tag)
                continue
            retval.append(plugin(config))
        return retval

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "paramtrigger"


PluginClass = ParameterizedBuildTrigger


if __name__ == "__main__":  # pragma: no cover
    pass
