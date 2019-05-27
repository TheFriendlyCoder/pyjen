"""Jenkins post-build publisher of type Parameterized Build Trigger"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import instantiate_xml_plugin


class ParameterizedBuildTrigger(XMLPlugin):
    """Custom job publisher that supports triggering other Jenkins jobs which
    require 1 or more custom build parameters

    https://plugins.jenkins.io/parameterized-trigger
    """

    @property
    def triggers(self):
        """list of trigger operations defined for this instance of the plugin

        :rtype: :class:`list` of :class:`BuildTriggerConfig` objects
        """
        retval = list()
        configs_node = self._root.find('configs')
        for cur_node in configs_node:

            plugin = instantiate_xml_plugin(cur_node, self)
            if plugin:
                retval.append(plugin)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.parameterizedtrigger.BuildTrigger"

    @classmethod
    def instantiate(cls, triggers):
        """Factory method for creating a new instances of this class

        :param list triggers:
            List of build trigger configuration objects
        :rtype: :class:`ParameterizedBuildTrigger`
        """
        default_xml = """
<hudson.plugins.parameterizedtrigger.BuildTrigger>
    <configs/>
</hudson.plugins.parameterizedtrigger.BuildTrigger>"""
        root_node = ElementTree.fromstring(default_xml)
        configs_node = root_node.find("configs")

        for cur_trig in triggers:
            configs_node.append(cur_trig.node)

        return cls(root_node)


PluginClass = ParameterizedBuildTrigger


if __name__ == "__main__":  # pragma: no cover
    pass
