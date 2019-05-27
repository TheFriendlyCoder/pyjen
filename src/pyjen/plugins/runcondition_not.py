"""Condition for the run condition plugin that inverts the logical result of
another build condition.
"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class NotCondition(XMLPlugin):
    """Condition for the run condition plugin that inverts the logical result
    of another build condition.

    https://plugins.jenkins.io/run-condition
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkins_ci.plugins.run_condition.logic.Not"

    @staticmethod
    def get_friendly_name():
        """Gets the user friendly display name for this condition

        This typically reflects the text found in the Jenkins UI for the
        condition

        :rtype: :class:`str`
        """
        return "not"

    @classmethod
    def instantiate(cls, condition):
        """Factory method that constructs an instance of this class

        :param condition:
            Any PyJen plugin compatible with the Run Condition plugin
        :rtype: :class:`NotCondition`
        """
        default_xml = '<condition class="{0}" plugin="run-condition@1.2"/>'
        default_xml = default_xml.format(cls.get_jenkins_plugin_name())
        root_node = ElementTree.fromstring(default_xml)
        root_node.append(condition.node)
        return cls(root_node)


PluginClass = NotCondition


if __name__ == "__main__":  # pragma: no cover
    pass
