"""Plugin for the Conditional Builder plugin that defines a conditional build
step that never executes regardless of any input condition
"""
import xml.etree.ElementTree as ElementTree
from pyjen.plugins.conditionalbuilder import ConditionalBuilderCondition


class NeverRun(ConditionalBuilderCondition):
    """Plugin for the Conditional Builder plugin that defines a conditional
    build step that never executes regardless of any input condition

    https://wiki.jenkins-ci.org/display/JENKINS/Conditional+BuildStep+Plugin
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkins_ci.plugins.run_condition.core.NeverRun"

    @staticmethod
    def get_friendly_name():
        """Gets the user friendly display name for this condition

        This typically reflects the text found in the Jenkins UI for the
        condition

        :rtype: :class:`str`
        """
        return "never"

    @classmethod
    def create(cls):
        default_xml = '<condition class="{0}" plugin="run-condition@1.2"/>'

        default_xml = default_xml.format(cls.get_jenkins_plugin_name())
        root_node = ElementTree.fromstring(default_xml)

        return cls(root_node)


PluginClass = NeverRun


if __name__ == "__main__":  # pragma: no cover
    pass
