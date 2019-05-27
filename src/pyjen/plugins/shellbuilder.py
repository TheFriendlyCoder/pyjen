"""Interface to control a basic shell build step job builder plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class ShellBuilder(XMLPlugin):
    """Interface to control a basic shell build step job builder plugin

    This plugin is a default, built-in plugin which is part of the Jenkins core
    """
    @property
    def script(self):
        """Gets the shell script associated with this builder

        :rtype: :class:`str`
        """

        command_node = self._root.find('command')
        return command_node.text

    @property
    def unstable_return_code(self):
        """Gets the return code that marks the build as unstable

        :rtype: :class:`int`
        """
        retval = self._root.findtext('unstableReturn')
        if not retval:
            return None
        return int(retval)

    @unstable_return_code.setter
    def unstable_return_code(self, value):
        """Changes the return code that marks the build as unstable"""
        rcode_node = self._root.find('unstableReturn')
        if not rcode_node:
            rcode_node = ElementTree.SubElement(self._root, "unstableReturn")
        rcode_node.text = str(value)
        self.update()

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.tasks.Shell"

    @classmethod
    def instantiate(cls, script):
        """Factory method for creating a new shell build step

        :param str script: shell script to run as part of this build step
        """
        default_xml = """<hudson.tasks.Shell></hudson.tasks.Shell>"""
        root_node = ElementTree.fromstring(default_xml)

        child = ElementTree.SubElement(root_node, "command")
        child.text = script

        return cls(root_node)


PluginClass = ShellBuilder


if __name__ == "__main__":  # pragma: no cover
    pass
