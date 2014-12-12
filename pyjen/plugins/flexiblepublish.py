"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
from pyjen.utils.pluginapi import find_xml_plugin, PluginBase, get_plugin_name
import xml.etree.ElementTree as ElementTree
import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


class FlexiblePublisher(PluginBase):
    """Publisher plugin enabling conditional execution of post-build steps in a Jenkins job"""
    type = "org.jenkins_ci.plugins.flexible_publish.FlexiblePublisher"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def actions(self):
        """Gets the list of publishers associated with this instance of the flexible publisher

        :returns: list of publishers associated with this instance of the flexible publisher
        :rtype: :class:`list` of Flexible Publish publishers such as :class:`ConditionalPublisher`
        """
        nodes = self._root.find("publishers")

        retval = []
        for node in nodes:
            plugin = find_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                log.warning("Flexible publisher plugin {0} not found".format(
                    get_plugin_name(node)))

        return retval


class ConditionalPublisher(PluginBase):
    """Interface to a single 'conditional' publisher contained within the flexible publish plugin"""
    type = "org.jenkins_ci.plugins.flexible_publish.ConditionalPublisher"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def publisher(self):
        """Retrieves the action to be performed when the conditions of this publisher are met

        :returns: list of PyJen objects which control each conditional action to be performed
        :rtype: :class:`list` of PyJen objects, typically one or more plugins supported by the Flexible Publish plugin
                Return None if an publisher plugin not currently supported by PyJen is being used
        """
        node = self._root.find("publisher")
        plugin = find_xml_plugin(node)

        if plugin is None:
            log.warning("Publisher plugin {0} referenced by Flexible Publisher not found".format(
                get_plugin_name(node)))

        return plugin

if __name__ == "__main__":  # pragma: no cover
    pass
