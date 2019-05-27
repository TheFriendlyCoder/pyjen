"""Interface to the Jenkins 'archive artifacts' publishing plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class ArtifactArchiverPublisher(XMLPlugin):
    """Interface to the Jenkins 'archive artifacts' publishing plugin

    This plugin is a default, built-in plugin which is part of the Jenkins core
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.tasks.ArtifactArchiver"

    @property
    def artifact_regex(self):
        """Gets the regular expression used to locate files to archive

        :rtype: :class:`str`
        """

        children_node = self._root.find('artifacts')
        return children_node.text

    @classmethod
    def instantiate(cls, file_pattern):
        """Factory method for creating a new artifact archiver

        :param str file_pattern:
            regular expression matching files to be archived at the end of
            the build
        :rtype:
            :class:`pyjen.plugins.artifactarchiver.ArtifactArchiverPublisher`
        """
        default_xml = """
<hudson.tasks.ArtifactArchiver>
    <allowEmptyArchive>false</allowEmptyArchive>
    <onlyIfSuccessful>false</onlyIfSuccessful>
    <fingerprint>false</fingerprint>
    <defaultExcludes>true</defaultExcludes>
    <caseSensitive>true</caseSensitive>
</hudson.tasks.ArtifactArchiver>"""
        root_node = ElementTree.fromstring(default_xml)
        child = ElementTree.SubElement(root_node, "artifacts")
        child.text = file_pattern

        return cls(root_node)


PluginClass = ArtifactArchiverPublisher


if __name__ == "__main__":  # pragma: no cover
    pass
