"""Primitives for operating on Jenkins job builder of type 'Conditional Builder'"""
from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name
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
        nodes = self._root.find("conditionalbuilders")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                log.warning("Builder plugin {0} used by conditional builder not found".format(get_plugin_name(node)))

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass

