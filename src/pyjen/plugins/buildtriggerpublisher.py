"""Interface to the Jenkins 'build trigger' publishing plugin"""
import xml.etree.ElementTree as ElementTree


class BuildTriggerPublisher:
    """Interface to the Jenkins 'build trigger' publishing plugin

    This plugin is a default, built-in plugin which is part of the Jenkins core
    """

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert self._root.tag == self.get_jenkins_plugin_name()

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.tasks.BuildTrigger"

    @property
    def job_names(self):
        """Gets the names of 0 or more downstream jobs managed by this config

        :rtype: :class:`list` of :class:`str`
        """

        children_node = self._root.find('childProjects')
        return [i.strip() for i in children_node.text.split(",")]

    @property
    def node(self):
        """Gets the XML node associated with this publisher

        :rtype: :class:`ElementTree.Element`
        """
        return self._root

    @staticmethod
    def create(project_name):
        """Factory method for creating a new build trigger

        The default trigger will run when the parent job is successful

        :param str project_name: name of the downstream job to be triggered
        :rtype: :class:`pyjen.plugins.buildtriggerpublisher.BuildTriggerPublisher`
        """
        default_xml = """<hudson.tasks.BuildTrigger>
<threshold>
<name>SUCCESS</name>
<ordinal>0</ordinal>
<color>BLUE</color>
<completeBuild>true</completeBuild>
</threshold>
</hudson.tasks.BuildTrigger>"""
        root_node = ElementTree.fromstring(default_xml)

        child = ElementTree.SubElement(root_node, "childProjects")
        child.text = project_name

        return BuildTriggerPublisher(root_node)


PluginClass = BuildTriggerPublisher


if __name__ == "__main__":  # pragma: no cover
    pass
