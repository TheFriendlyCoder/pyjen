"""Primitives for operating on properties of the 'artifact deployer' publishing plugin"""
from pyjen.utils.pluginapi import get_plugins, PluginBase, PluginXML
from pyjen.exceptions import PluginNotSupportedError
import xml.etree.ElementTree as ElementTree


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

        entries_node = self._root.find("entries")

        retval = []
        for cur_entry in entries_node:
            configxml = ElementTree.tostring(cur_entry, "UTF-8").decode("utf-8")
            pluginxml = PluginXML(configxml)

            plugin_obj = None
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    plugin_obj = plugin(cur_entry)
                    break

            if plugin_obj is None:
                raise PluginNotSupportedError("Artifact deployer configuration plugin {0} not found".format(pluginxml.get_class_name()),
                                              pluginxml.get_class_name())

            retval.append(plugin_obj)
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

