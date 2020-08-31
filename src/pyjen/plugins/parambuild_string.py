"""String build parameter - plugin for parameterized build plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class ParameterizedBuildStringParameter(XMLPlugin):
    """String build parameter - plugin for parameterized build plugin"""
    @property
    def name(self):
        """Gets the friendly name assigned to this parameter

        :rtype: :class:`str`
        """
        node = self._root.find("name")
        assert node is not None
        return node.text

    @property
    def description(self):
        """str: the descriptive text associated with this parameter"""
        node = self._root.find("description")
        assert node is not None
        return node.text

    @property
    def default_value(self):
        """str: the default value for this parameter"""
        node = self._root.find("defaultValue")
        assert node is not None
        return node.text

    @property
    def trim(self):
        """bool: Checks to see if the value for this parameter should have
        whitespace stripped from the start and end automatically"""
        node = self._root.find("trim")
        assert node is not None
        return node.text.lower().strip() == "true"

    # --------------------------------------------------------------- PLUGIN API
    @classmethod
    def instantiate(cls, name, default_value, description, trim):
        """Factory method for creating a new string build parameter

        Args:
            name (str):
                Friendly name to give this build parameter
            default_value (str):
                Text to assign this parameter when no user defined value is
                given
            description (str):
                Descriptive text to show on the Jenkins UI explaining the
                purpose of this parameter
            trim (bool):
                Indicates whether leading and trailing whitespace should be
                stripped from values entered into this field at build time

        Returns:
            ParameterizedBuildStringParameter:
                instance of this class
        """
        default_xml = """<hudson.model.StringParameterDefinition>
</hudson.model.StringParameterDefinition>"""
        root_node = ElementTree.fromstring(default_xml)

        name_node = ElementTree.SubElement(root_node, "name")
        name_node.text = name

        desc_node = ElementTree.SubElement(root_node, "description")
        desc_node.text = description

        default_val_node = ElementTree.SubElement(root_node, "defaultValue")
        default_val_node.text = default_value

        trim_node = ElementTree.SubElement(root_node, "trim")
        trim_node.text = str(trim)

        return cls(root_node)

    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.model.StringParameterDefinition"


PluginClass = ParameterizedBuildStringParameter


if __name__ == "__main__":  # pragma: no cover
    pass
