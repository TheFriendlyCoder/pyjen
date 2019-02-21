"""Primitives for operating on Jenkins job builder of type 'Conditional Builder'
"""
import logging
#from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name

# TODO: Have a separate entry point for these plugins, and instantiate different
#       classes depending on whether we have a single conditional build step or
#       a multiple conditional build step the ConditionalBuilder class would
#       map to the latter from the looks of it

# TODO: Consider having most of these XML based plugins derive from ConfigXML
#       class so they can use methods like plugin_name, plugin_version, etc.


class ConditionalBuilder(object):
    """Jenkins job builder plugin

    capable of conditionally executing a build operation

    https://wiki.jenkins-ci.org/display/JENKINS/Conditional+BuildStep+Plugin
    """

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert 'plugin' in self._root.attrib
        assert self._root.attrib['plugin'].startswith('conditional-buildstep')
        self._log = logging.getLogger(__name__)

    @property
    def builders(self):
        """list of the build operators that will be executed if the conditions
        on this builder are satisfied

        :returns: list of build operators
        :rtype: :class:`list` of PyJen plugins
        """
        nodes = self._root.find("conditionalbuilders")

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Builder plugin %s used by conditional "
                                  "builder not found", get_plugin_name(node))

        return retval

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "conditionalbuilder"

PluginClass = ConditionalBuilder


if __name__ == "__main__":  # pragma: no cover
    pass
