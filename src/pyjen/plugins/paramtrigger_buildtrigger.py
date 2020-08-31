"""Trigger configuration for a parameterized build trigger"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin
from pyjen.utils.plugin_api import instantiate_xml_plugin


class BuildTriggerConfig(XMLPlugin):
    """Contains the configuration options for a single downstream build trigger
    compatible with the parameterized build trigger plugin

    https://plugins.jenkins.io/parameterized-trigger
    """
    @property
    def condition(self):
        """str: The state the current job must be in before the downstream job
        will be triggered"""
        node = self._root.find('condition')
        return node.text

    @property
    def job_names(self):
        """list (str): list of the names of downstream jobs to be triggered"""
        node = self.node.find("projects")
        retval = node.text.split(",")
        return [i.strip() for i in retval]

    @property
    def build_params(self):
        """list (XMLPlugin): List of parameter definitions used to configure
        the build trigger for the downstream jobs associated with this trigger

        Each element in the list may be of any number of derived types, each
        supporting a different type of custom behavior on how the parameters
        for the downstream job should be created / set.
        """
        retval = list()
        node = self.node.find("configs")
        for cur_child in node:
            plugin = instantiate_xml_plugin(cur_child, self)
            if plugin:
                retval.append(plugin)
        return retval

    def add_build_param(self, param_config):
        """Adds a new configuration option for customizing the build parameters
        passed to the jobs that are triggered by this configuration

        Args:
            param_config (XMLPlugin):
                One of several supported plugins which offer unique
                customizations on how build parameters for the downstream jobs
                being triggered
        """
        parent = self.node.find("configs")
        parent.append(param_config.node)
        param_config.parent = self

    @classmethod
    def instantiate(cls, job_names):
        """Factory method for creating a new instances of this class

        Args:
            job_names (:class:`list` of :class:`str`):
                List of the names of 1 or more Jenkins jobs to be triggered by
                this configuration object

        Returns:
            BuildTriggerConfig:
                instance of this class
        """
        default_xml = """
<hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
    <configs/>
    <projects/>
    <condition>SUCCESS</condition>
    <triggerWithNoParameters>true</triggerWithNoParameters>
    <triggerFromChildProjects>false</triggerFromChildProjects>
</hudson.plugins.parameterizedtrigger.BuildTriggerConfig>"""
        root_node = ElementTree.fromstring(default_xml)
        projects_node = root_node.find("projects")
        projects_node.text = ",".join(job_names)
        return cls(root_node)

    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.plugins.parameterizedtrigger.BuildTriggerConfig"


PluginClass = BuildTriggerConfig


if __name__ == "__main__":  # pragma: no cover
    pass
