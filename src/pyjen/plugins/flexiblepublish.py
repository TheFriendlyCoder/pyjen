"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import instantiate_xml_plugin


class FlexiblePublisher(XMLPlugin):
    """Job plugin enabling conditional execution of post-build steps

    https://plugins.jenkins.io/flexible-publish
    """

    @property
    def actions(self):
        """list of conditional actions associated with this instance

        :rtype: :class:`list` of :class:`ConditionalAction`
        """
        nodes = self._root.find("publishers")

        retval = list()
        for cur_node in nodes:
            temp = ConditionalAction(cur_node)
            temp.parent = self
            retval.append(temp)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkins_ci.plugins.flexible_publish.FlexiblePublisher"

    @classmethod
    def instantiate(cls, actions):
        """Factory method for creating a new instances of this class

        :param actions:
            list of conditional actions to perform under this publisher
        :type actions:
            :class:`list` of :class:`ConditionalAction`
        :rtype: :class:`ParameterizedBuildTrigger`
        """
        default_xml = """
<org.jenkins__ci.plugins.flexible__publish.FlexiblePublisher>
    <publishers/>
</org.jenkins__ci.plugins.flexible__publish.FlexiblePublisher>"""
        root_node = ElementTree.fromstring(default_xml)
        configs_node = root_node.find("publishers")

        for cur_action in actions:
            configs_node.append(cur_action.node)

        return cls(root_node)


class ConditionalAction(XMLPlugin):
    """conditional action associated with a flexible publisher

    Contains 1 or more publishers to be run if a certain set of
    conditions is met.
    """

    @property
    def publishers(self):
        """List of publishers to run should the conditions associated with this
        action are met

        :rtype: :class:`list`
        """
        nodes = self._root.find("publisherList")
        retval = list()
        for cur_node in nodes:
            plugin = instantiate_xml_plugin(cur_node, self)
            if plugin:
                retval.append(plugin)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @classmethod
    def instantiate(cls, condition, actions):
        """Factory method for creating a new instances of this class

        :param condition:
            Flexible publish build condition pre-configured to control
            this publish operation
        :param list actions:
            List of 1 or more "build stage" plugins that you would like to use
            in the publish phase of a Jenkins job
        :rtype: :class:`ConditionalPublisher`
        """
        default_xml = """
<org.jenkins__ci.plugins.flexible__publish.ConditionalPublisher>
    <publisherList/>
    <runner class="org.jenkins_ci.plugins.run_condition.BuildStepRunner$Fail" />
    <executionStrategy class="org.jenkins_ci.plugins.flexible_publish.strategy.FailAtEndExecutionStrategy"/>
</org.jenkins__ci.plugins.flexible__publish.ConditionalPublisher>
"""  # pylint: disable=line-too-long
        root_node = ElementTree.fromstring(default_xml)
        root_node.append(condition.node)
        configs_node = root_node.find("publisherList")

        for cur_action in actions:
            configs_node.append(cur_action.node)

        return cls(root_node)


PluginClass = FlexiblePublisher


if __name__ == "__main__":  # pragma: no cover
    pass
