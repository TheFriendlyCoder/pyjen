"""Primitives for operating on Jenkins job builder of type 'Conditional Builder'"""
import logging
from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name


class ConditionalBuilder:
    """Jenkins job builder plugin capable of conditionally executing a build operation"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        self._log = logging.getLogger(__name__)

    @property
    def builders(self):
        """Gets a list of the build operators that will be executed if the conditions on this
        builder are satisfied

        :returns: list of build operators
        :rtype: :class:`list` of PyJen plugins that support the Jenkins builder operations
        """
        nodes = self._root.find("conditionalbuilders")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Builder plugin %s used by conditional builder not found", get_plugin_name(node))

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
