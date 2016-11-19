"""Primitives for operating on properties of the 'artifact deployer' publishing plugin"""
from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name
from pyjen.exceptions import PluginNotSupportedError


class ArtifactDeployer(PluginBase):
    """Interface to the Jenkins 'artifact deployer' publishing plugin"""
    type = "org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerPublisher"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def entries(self):
        """Gets the list of deployment options associated with this plugin

        :returns: list of configuration options for each set of artifacts managed by this instance
        :rtype: :class:`list` of :class:`ArtifactDeployerEntry` objects
        """

        nodes = self._root.find("entries")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                raise PluginNotSupportedError("Artifact deployer configuration plugin {0} not found".format(
                    get_plugin_name(node)), get_plugin_name(node))

        return retval


class ArtifactDeployerEntry(PluginBase):
    """Interface to a single configuration of artifacts to be deployed by an Artifact Deployer instance"""
    type = "org.jenkinsci.plugins.artifactdeployer.ArtifactDeployerEntry"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def remote(self):
        """Gets the remote location where these artifacts are to be published

        :rtype: :class:`str`
        """
        node = self._root.find("remote")
        return node.text

if __name__ == "__main__":  # pragma: no cover
    pass
