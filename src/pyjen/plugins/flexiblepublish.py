"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
from xml.etree import ElementTree
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import instantiate_xml_plugin


class FlexiblePublisher(XMLPlugin):
    """Job plugin enabling conditional execution of post-build steps

    https://plugins.jenkins.io/flexible-publish
    """

    @property
    def actions(self):
        """list (ConditionalAction): list of conditional actions associated with
         this publisher"""
        nodes = self._root.find("publishers")

        retval = []
        for cur_node in nodes:
            temp = ConditionalAction(cur_node)
            temp.parent = self
            retval.append(temp)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "org.jenkins_ci.plugins.flexible_publish.FlexiblePublisher"

    @classmethod
    def instantiate(cls, actions):
        """Factory method for creating a new instances of this class

        Args:
            actions (:class:`list` of :class:`ConditionalAction`):
                list of conditional actions to perform under this publisher
        Returns:
            FlexiblePublisher:
                reference to the newly instantiated object
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
        """list (XMLPlugin): publishers to run should the conditions associated
        with this action are met"""
        nodes = self._root.find("publisherList")
        retval = []
        for cur_node in nodes:
            plugin = instantiate_xml_plugin(cur_node, self)
            if plugin:
                retval.append(plugin)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @classmethod
    def instantiate(cls, condition, actions):
        """Factory method for creating a new instances of this class

        Args:
            condition (XMLPlugin):
                Flexible publish build condition pre-configured to control
                this publish operation
            actions (:class:`list` of :class:`~.utils.xml_plugin.XMLPlugin`):
                List of 1 or more "build stage" plugins that you would like to
                use in the publish phase of a Jenkins job

        Returns:
            ConditionalAction:
                reference to the newly instantiated object
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
