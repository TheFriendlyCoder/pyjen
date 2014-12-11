"""Primitives for operating on job publishers of type 'Flexible Publisher'"""
from pyjen.utils.pluginapi import get_plugins, PluginBase, PluginXML
from pyjen.exceptions import PluginNotSupportedError
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
        publishers_node = self._root.find("publishers")

        retval = []
        for cur_publisher in publishers_node:
            configxml = ElementTree.tostring(cur_publisher, "UTF-8").decode("utf-8")
            pluginxml = PluginXML(configxml)

            plugin_obj = None
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    plugin_obj = plugin(cur_publisher)
                    break

            if plugin_obj is None:
                raise PluginNotSupportedError("Flexible publisher plugin {0} not found".format(pluginxml.get_class_name()),
                                              pluginxml.get_class_name())

            retval.append(plugin_obj)
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
        publisher_node = self._root.find("publisher")

        configxml = ElementTree.tostring(publisher_node, "UTF-8").decode("utf-8")
        pluginxml = PluginXML(configxml)

        plugin_obj = None
        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                plugin_obj = plugin(publisher_node)
                break

        if plugin_obj is None:
            log.warning("Publisher plugin {0} referenced by Flexible Publisher not found".format(pluginxml.get_class_name()))

        return plugin_obj

if __name__ == "__main__":  # pragma: no cover
    pass
