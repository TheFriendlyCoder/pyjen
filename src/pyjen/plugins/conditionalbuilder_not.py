"""Plugin for the Conditional Builder plugin that defines a conditional build
step that performs a logical NOT operation on another condition
"""
import xml.etree.ElementTree as ElementTree
from pyjen.plugins.conditionalbuilder import ConditionalBuilderCondition


class NotCondition(ConditionalBuilderCondition):
    """Plugin for the Conditional Builder plugin that defines a conditional
    build step that performs a logical NOT operation on another condition

    https://wiki.jenkins-ci.org/display/JENKINS/Conditional+BuildStep+Plugin
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
    def create(cls, condition):
        """Creates a new instance of this condition

        :param condition:
            Condition to be negated
        :type condition:
            :class:`~.conditionalbuilder.ConditionalBuilderCondition`
        :rtype: :class:`~.And`
        """
        default_xml = '<condition class="{0}" plugin="run-condition@1.2"/>'
        default_xml = default_xml.format(cls.get_jenkins_plugin_name())
        root_node = ElementTree.fromstring(default_xml)
        root_node.append(condition.node)
        return cls(root_node)


PluginClass = NotCondition


if __name__ == "__main__":  # pragma: no cover
    pass
