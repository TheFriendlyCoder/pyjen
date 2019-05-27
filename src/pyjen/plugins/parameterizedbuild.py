"""Implementation for the parameterized build plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import instantiate_xml_plugin


class ParameterizedBuild(XMLPlugin):
    """Plugin which allows custom build paramters to be passed to a job"""
    @property
    def parameters(self):
        """Gets a list of the build parameters associated with this property

        :rtype: :class:`list` of build parameters
        """
        params_node = self._root.find("parameterDefinitions")
        assert params_node is not None
        retval = list()
        for cur_param in params_node:
            plugin = instantiate_xml_plugin(cur_param, self)
            if plugin:
                retval.append(plugin)
        return retval

    # --------------------------------------------------------------- PLUGIN API
    @classmethod
    def instantiate(cls, params):
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
