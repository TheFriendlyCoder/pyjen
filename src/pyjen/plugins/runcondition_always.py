"""Condition for the run condition plugin that will always produce a true result
"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class AlwaysRun(XMLPlugin):
    """Conditional build step that will always produce a true result

    https://plugins.jenkins.io/run-condition
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkins_ci.plugins.run_condition.core.AlwaysRun"

    @staticmethod
    def get_friendly_name():
        """Gets the user friendly display name for this condition

        This typically reflects the text found in the Jenkins UI for the
        condition

        :rtype: :class:`str`
        """
        return "always"

    @classmethod
    def instantiate(cls):
        """Factory method used to construct an instance of this class

        :rtype: :class:`AlwaysRun`
        """
        default_xml = '<condition class="{0}" plugin="run-condition@1.2"/>'
        default_xml = default_xml.format(cls.get_jenkins_plugin_name())
        root_node = ElementTree.fromstring(default_xml)

        return cls(root_node)


PluginClass = AlwaysRun


if __name__ == "__main__":  # pragma: no cover
    pass
