"""Primitives for interacting with the PyJen plugin API"""
import logging
import xml.etree.ElementTree as ElementTree
from pkg_resources import iter_entry_points
from pyjen.exceptions import PluginNotSupportedError


class PluginAPI(object):
    """Base class for all PyJen extensions wrapping specific Jenkins plugins

    Plugins are defined by an XML node with attributes describing the plugin associated with the XML and 0 or more
    child elements containing the parameters used by the plugin. The XML representation of a plugin is expected
    to conform to one of the following patterns:

    * <com.tikal.jenkins.plugins.multijob.MultiJobProject plugin="jenkins-multijob-plugin@1.20">
    * <logRotator class="hudson.tasks.LogRotator">
    * <hudson.model.ListView>

    The first example defines the "friendly" name of the plugin and it's associated version number using the pattern
    "plugin_name@version". The second example stores the Java class name associated with the Jenkins plugin itself.
    The last example illustrates how some of the built-in types are defined by naming the root tag with the full
    Java class name, which appears to be analogous to the 'class' attribute from example 2.

    :param str config_xml: Plain text XML of the plugin to be instantiated
    :param str url:
        full REST API endpoint of the Jenkins object associated with the XML
        may be omitted for nested XML-based plugins with no explicit REST API endpoint

    """
    def __init__(self, config_xml, url=None):
        self._root = ElementTree.fromstring(config_xml)
        self._log = logging.getLogger(__name__)
        self._url = url

    @property
    def plugin_name(self):
        """Gets the name of the plugin

        :returns: the plugin name if one is defined, otherwise None
        :rtype: :class:`str`
        """
        if 'plugin' not in self._root.attrib:
            return None

        attr = self._root.attrib['plugin']
        if '@' not in attr:
            raise ValueError('Jenkins plugin attributes are expected to be of the form "name@version": {0}'.format(attr))

        parts = attr.split('@')

        return parts[0]

    @property
    def class_name(self):
        """Gets the Java class name of the plugin

        :returns: the Java class name
        :rtype: :class:`str`
        """

        if "class" in self._root.attrib:
            return self._root.attrib['class']
        else:
            return self._root.tag

    @property
    def version(self):
        """Gets the version of the plugin

        :returns: the plugin version
        :rtype: :class:`str`
        """
        if 'plugin' not in self._root.attrib:
            return None

        attr = self._root.attrib['plugin']
        if '@' not in attr:
            raise ValueError('Jenkins plugin attributes are expected to be of the form "name@version": {0}'.format(attr))

        parts = attr.split('@')
        return parts[1]

    def _find_plugin(self):
        """Locates a PyJen plugin of the given type

        :param str plugin_type: the descriptive type-name for the plugin to find
        :returns: reference to the plugin class for the specified type, or None if a compatible plugin could not be found
        """
        entry_point_name = self.plugin_name or self.class_name
        if entry_point_name is None:
            raise Exception("Parsing error: no valid Jenkins plugin name could be parsed from provided XML")

        tmp_log = logging.getLogger(__name__)
        supported_plugins = []
        for entry_point in iter_entry_points(group='pyjen.plugins', name=entry_point_name):
            supported_plugins.append(entry_point.load())

        if len(supported_plugins) == 0:
            raise PluginNotSupportedError("Plugin not supported: " + entry_point_name)

        if len(supported_plugins) > 1:
            tmp_log.warning("multiple plugins detected for specified Jenkins object: %s. Using first match.",
                            entry_point_name)

        return supported_plugins[0]

    def init_plugin(self):
        """Instantiates a PyJen plugin that wraps a particular Jenkins plugin"""

        plugin_class = self._find_plugin()

        if self._url:
            return plugin_class(self._url)
        else:
            return plugin_class(self.config_xml)

    @staticmethod
    def get_installed_plugins():
        retval = []
        for ep in iter_entry_points(group='pyjen.plugins', name=None):
            retval.append(ep.name)
        return retval

if __name__ == "__main__":  # pragma: no cover
    # print a list of all installed PyJen plugins
    # plugins = PluginAPI.get_installed_plugins()
    # for p in plugins:
    #       print (p)
    pass
