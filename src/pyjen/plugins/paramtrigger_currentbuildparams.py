"""Trigger parameter for the Parameterized Trigger plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class CurrentBuildParams(XMLPlugin):
    """Passes the current build parameters along to a parameterized downstream
    job
    """

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.parameterizedtrigger.CurrentBuildParameters"

    @classmethod
    def instantiate(cls):
        """Factory method for creating a new instances of this class

        :rtype: :class:`CurrentBuildParams`
        """
        default_xml = \
            """<hudson.plugins.parameterizedtrigger.CurrentBuildParameters/>"""
        root_node = ElementTree.fromstring(default_xml)
        return cls(root_node)


PluginClass = CurrentBuildParams


if __name__ == "__main__":  # pragma: no cover
    pass
