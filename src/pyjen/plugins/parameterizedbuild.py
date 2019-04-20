import logging
import xml.etree.ElementTree as ElementTree
from pyjen.utils.plugin_api import find_plugin


class ParameterizedBuild(object):
    def __init__(self, node):
        self._node = node
        self._log = logging.getLogger(__name__)

    @property
    def node(self):
        """Gets the raw XML node defining the configuration for this plugin"""
        return self._node

    @property
    def parameters(self):
        """Gets a list of the build parameters associated with this property

        :rtype: :class:`list` of build parameters
        """
        params_node = self._node.find("parameterDefinitions")
        assert params_node is not None
        retval = list()
        for cur_param in params_node:
            plugin = find_plugin(cur_param.tag)

            if plugin is None:
                self._log.warning(
                    "Skipping unsupported plugin: %s", cur_param.tag)
                continue

            retval.append(plugin(cur_param))
        return retval

    @classmethod
    def create(cls, params):
        """Factory method for this class

        :param list params:
            List of parameters to add to this build property
            Each element must be associated with a parameter type supported
            by the parameterized build plugin
        :returns: an instance of this class
        :rtype: :class:`ParameterizedBuild`
        """
        default_xml = """<hudson.model.ParametersDefinitionProperty>
</hudson.model.ParametersDefinitionProperty>
"""
        root_node = ElementTree.fromstring(default_xml)
        params_node = ElementTree.SubElement(root_node, "parameterDefinitions")
        for cur_child in params:
            params_node.append(cur_child.node)
        return cls(root_node)

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.model.ParametersDefinitionProperty"


PluginClass = ParameterizedBuild


if __name__ == "__main__":  # pragma: no cover
    pass
