"""Primitives for operating on Jenkins job builder of type 'Conditional Builder'"""
from pyjen.utils.pluginapi import get_plugins, PluginBase, PluginXML
from pyjen.exceptions import PluginNotSupportedError
import xml.etree.ElementTree as ElementTree
import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


class ConditionalBuilder(PluginBase):
    """Jenkins job builder plugin capable of conditionally executing a build operation"""
    type = "org.jenkinsci.plugins.conditionalbuildstep.ConditionalBuilder"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def builders(self):
        """Gets a list of the build operators that will be executed if the conditions on this
        builder are satisfied

        :returns: list of build operators
        :rtype: :class:`list` of PyJen plugins that support the Jenkins builder operations
        """
        builders_node = self._root.find("conditionalbuilders")

        retval = []
        for cur_builder in builders_node:
            builder_plugin = self._locate_builder(cur_builder)
            if builder_plugin is not None:
                retval.append(builder_plugin)
        return retval

    def _locate_builder(self, xml_node):
        """Helper function that locates and loads plugins called by the conditional builder

        :param xml_node: Descriptive XML node for the builder to find
        :type xml_node: :class:`ElementTree.Element`
        :returns: builder plugin associated with this node, or None if plugin not supported
        :rtype: One of any of the support PyJen plugins
        """
        configxml = ElementTree.tostring(xml_node, "UTF-8").decode("utf-8")
        pluginxml = PluginXML(configxml)

        plugin_obj = None
        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                plugin_obj = plugin(xml_node)
                break

        if plugin_obj is None:
            log.warning("Builder plugin {0} used by conditional builder not found".format(pluginxml.get_class_name()))

        return plugin_obj

if __name__ == "__main__":  # pragma: no cover
    pass

