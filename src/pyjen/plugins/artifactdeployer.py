"""properties of the 'artifact deployer' publishing plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class ArtifactDeployer(XMLPlugin):
    """Interface to the Jenkins 'artifact deployer' publishing plugin

    https://plugins.jenkins.io/artifactdeployer
    """

    @classmethod
    def instantiate(cls):
        """Factory method for creating a new artifact deployer
        :rtype: :class:`pyjen.plugins.artifactdeployer.ArtifactDeployer`
        """
        default_xml = """
<org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerPublisher>
    <entries class="empty-list"/>
    <deployEvenBuildFail>false</deployEvenBuildFail>
</org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerPublisher>"""
        root_node = ElementTree.fromstring(default_xml)

        return cls(root_node)

    @property
    def entries(self):
        """Gets the list of deployment options associated with this plugin

        :returns:
            list of configuration options for each set of artifacts managed by
            this instance
        :rtype: :class:`list` of :class:`ArtifactDeployerEntry` objects
        """

        nodes = self._root.find("entries")

        retval = list()
        for node in nodes:
            retval.append(ArtifactDeployerEntry(node))

        return retval

    def add_entry(self, new_entry):
        """Adds a new deployer entry to this publisher

        :param new_entry:
            New publisher descriptor entry to be added
        :type new_entry: :class:`~.ArtifactDeployerEntry`
        """
        entries_node = self._root.find('entries')
        entries_node.append(new_entry.node)
        new_entry.parent = self
        self.update()

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return \
            "org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerPublisher"


class ArtifactDeployerEntry(XMLPlugin):
    """a single artifacts to be deployed by an Artifact Deployer instance"""
    @classmethod
    def instantiate(cls, include_pattern, remote_path):
        """Factory method used to instantiate instances of this class

        :param str include_pattern:
            Path or regular expression of the file(s) to be published
        :param str remote_path:
            Path to remote share where files are to be published
        :returns:
            instance of the artifact deployer entry
        :rtype: :class:`ArtifactDeployerEntry`
        """
        default_xml = """
<org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerEntry>
    <basedir/>
    <excludes/>
    <flatten>false</flatten>
    <deleteRemote>false</deleteRemote>
    <deleteRemoteArtifacts>false</deleteRemoteArtifacts>
    <failNoFilesDeploy>false</failNoFilesDeploy>
</org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerEntry>"""

        root_node = ElementTree.fromstring(default_xml)
        includes_node = ElementTree.SubElement(root_node, "includes")
        includes_node.text = include_pattern
        remote_node = ElementTree.SubElement(root_node, "remote")
        remote_node.text = remote_path

        return cls(root_node)

    @property
    def remote(self):
        """Gets the remote location where these artifacts are to be published

        :rtype: :class:`str`
        """
        node = self._root.find("remote")
        return node.text

    @property
    def includes(self):
        """Gets the path or regular expression describing files to be published

        :rtype: :class:`str`
        """
        node = self._root.find("includes")
        return node.text


PluginClass = ArtifactDeployer


if __name__ == "__main__":  # pragma: no cover
    pass
