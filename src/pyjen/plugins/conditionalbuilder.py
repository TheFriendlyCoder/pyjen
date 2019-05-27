"""Primitives for operating on Jenkins job builder of type 'Conditional Builder'
"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.plugin_api import find_plugin
from pyjen.utils.xml_plugin import XMLPlugin


class ConditionalBuilder(XMLPlugin):
    """Jenkins job builder plugin

    capable of conditionally executing a build operation

    https://wiki.jenkins-ci.org/display/JENKINS/Conditional+BuildStep+Plugin
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkinsci.plugins.conditionalbuildstep.singlestep." \
               "SingleConditionalBuilder"

    @classmethod
    def instantiate(cls, condition, builder):
        """Factory method for creating a new conditional build step

        :param builder:
            Nested job build step to be executed conditionally
            May be any PyJen plugin that defines / manages a Job build step
        :param condition:
            Condition to be applied to the build step. The build step will only
            be executed if the terms defined by this condition evaluate to True
        :type condition: :class:`~.ConditionalBuilderCondition`
        :returns: newly created conditional build step
        :rtype: :class:`~.ConditionalBuilder`
        """
        # TODO: add support for multi-condition builder
        default_xml = """
<org.jenkinsci.plugins.conditionalbuildstep.singlestep.SingleConditionalBuilder>
    <runner class="org.jenkins_ci.plugins.run_condition.BuildStepRunner$Fail"/>
</org.jenkinsci.plugins.conditionalbuildstep.singlestep.SingleConditionalBuilder>
"""  # pylint: disable=line-too-long

        root_node = ElementTree.fromstring(default_xml)
        root_node.append(condition.node)
        build_step = ElementTree.SubElement(root_node, "buildStep")

        # The XML for the build step, unfortunately, doesn't match the original
        # XML when it gets nested inside the conditional build plugin. The
        # root node is hidden in the "class" attribute of the "buildStep" node,
        # and all further child nodes in the original XML are transposed under
        # the "buildStep" node. The final result should look something like this
        #
        # Original builder XML:
        # <MyCustomBuilder>
        #     <Node1FromCustomBuilder>...</Node1FromCustomBuilder>
        #     <Node2FromCustomBuilder>...</Node2FromCustomBuilder>
        # </MyCustomBuilder>
        #
        # New, nested, conditional builder XML:
        # <buildStep class="MyCustomBuilder">
        #     <Node1FromCustomBuilder>...</Node1FromCustomBuilder>
        #     <Node2FromCustomBuilder>...</Node2FromCustomBuilder>
        # </buildStep>
        #
        build_step.attrib["class"] = builder.node.tag
        for cur_child in builder.node:
            build_step.append(cur_child)

        return cls(root_node)

    @property
    def condition(self):
        """Gets the object describing the conditions for this build step"""
        node = self._root.find("condition")
        assert node is not None
        plugin = find_plugin(node.attrib["class"])
        if not plugin:
            msg = "Conditional build step condition {0} not supported by PyJen."
            raise NotImplementedError(msg.format(node.attrib["class"]))
        return plugin(node)

    @property
    def builder(self):
        """Gets the build step managed by this condition
        """
        build_step_node = self._root.find("buildStep")
        plugin = find_plugin(build_step_node.attrib["class"])
        if not plugin:
            raise NotImplementedError(
                "Build step plugin {0} is not supported by PyJen.".format(
                    build_step_node.attrib["class"]
                )
            )

        # We have to reconstruct the XML for the build step from the
        # encoded version in the buildStep. For further details see
        # the encoding logic found in the create() method of this class.
        root_node = ElementTree.Element(build_step_node.attrib["class"])
        for cur_child in build_step_node:
            root_node.append(cur_child)

        return plugin(root_node)


PluginClass = ConditionalBuilder


if __name__ == "__main__":  # pragma: no cover
    pass
