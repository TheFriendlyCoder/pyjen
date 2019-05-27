"""Condition for the run condition plugin that performs a logical AND operation
on other build conditions
"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class AndCondition(XMLPlugin):
    """Build condition that combines 2 or more other conditions with a logical
    AND operation. The associated operation using this condition will only run
    if all of the contained conditions result in a "true" value.

    https://plugins.jenkins.io/run-condition
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkins_ci.plugins.run_condition.logic.And"

    @staticmethod
    def get_friendly_name():
        """Gets the user friendly display name for this condition

        This typically reflects the text found in the Jenkins UI for the
        condition

        :rtype: :class:`str`
        """
        return "and"

    @classmethod
    def instantiate(cls, terms):
        """Creates a new instance of this condition

        :param list terms:
            List of 2 or more conditions to be combined using a logical AND
            operation. Each element is expected to be an instance of a PyJen
            plugin compatible with the Run Condition plugin.
        :rtype: :class:`AndCondition`
        """
        assert len(terms) >= 2

        default_xml = '<condition class="{0}" plugin="run-condition@1.2"/>'
        default_xml = default_xml.format(cls.get_jenkins_plugin_name())
        root_node = ElementTree.fromstring(default_xml)
        conditions_node = ElementTree.SubElement(root_node, "conditions")
        for cur_term in terms:
            term_node = ElementTree.Element(
                "org.jenkins_ci.plugins.run_condition.logic.ConditionContainer"
            )
            term_node.append(cur_term.node)
            conditions_node.append(term_node)
        return cls(root_node)


PluginClass = AndCondition


if __name__ == "__main__":  # pragma: no cover
    pass
