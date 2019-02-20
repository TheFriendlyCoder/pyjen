"""Interface to control a basic shell build step job builder plugin"""
import xml.etree.ElementTree as ElementTree


class ShellBuilder:
    """Interface to control a basic shell build step job builder plugin

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
        return "hudson.tasks.Shell"

    @property
    def script(self):
        """Gets the shell script associated with this builder

        :rtype: :class:`str`
        """

        command_node = self._root.find('command')
        return command_node.text

    @property
    def node(self):
        """Gets the XML node associated with this publisher

        :rtype: :class:`ElementTree.Element`
        """
        return self._root

    @staticmethod
    def create(script):
        """Factory method for creating a new shell build step

        :param str script: shell script to run as part of this build step
        """
        default_xml = """<hudson.tasks.Shell>
</hudson.tasks.Shell>"""
        root_node = ElementTree.fromstring(default_xml)

        child = ElementTree.SubElement(root_node, "command")
        child.text = script

        return ShellBuilder(root_node)


PluginClass = ShellBuilder


if __name__ == "__main__":  # pragma: no cover
    pass


