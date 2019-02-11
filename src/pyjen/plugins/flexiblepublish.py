"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
import logging
from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name


class FlexiblePublisher:
    """Publisher plugin enabling conditional execution of post-build steps in a Jenkins job

    https://wiki.jenkins-ci.org/display/JENKINS/Flexible+Publish+Plugin
    """

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert 'plugin' in self._root.attrib
        assert self._root.attrib['plugin'].startswith('flexible-publish')
        self._log = logging.getLogger(__name__)

    @property
    def actions(self):
        """Gets the list of publishers associated with this instance of the flexible publisher

        :returns: list of publishers associated with this instance of the flexible publisher
        :rtype: :class:`list` of Flexible Publish publishers such as :class:`ConditionalPublisher`
        """
        nodes = self._root.find("publishers")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Flexible publisher plugin %s not found", get_plugin_name(node))

        return retval


class ConditionalPublisher:
    """Interface to a single 'conditional' publisher contained within the flexible publish plugin"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert self._root.tag == 'org.jenkins__ci.plugins.flexible__publish.ConditionalPublisher'
        self._log = logging.getLogger(__name__)

    @property
    def publisher(self):
        """Retrieves the action to be performed when the conditions of this publisher are met

        :returns: list of PyJen objects which control each conditional action to be performed
        :rtype: :class:`list` of PyJen objects, typically one or more plugins supported by the Flexible Publish plugin
                Return None if an publisher plugin not currently supported by PyJen is being used
        """
        node = self._root.find("publisher")
        plugin = create_xml_plugin(node)

        if plugin is None:
            self._log.warning("Publisher plugin %s referenced by Flexible Publisher not found", get_plugin_name(node))

        return plugin

if __name__ == "__main__":  # pragma: no cover
    pass
