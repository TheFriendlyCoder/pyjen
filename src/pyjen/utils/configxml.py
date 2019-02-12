"""Common functionality for parsing and processing Jenkins raw configuration XML for various REST API objects"""
import logging
import xml.etree.ElementTree as ElementTree
from pkg_resources import iter_entry_points
from pyjen.exceptions import PluginNotSupportedError


class ConfigXML(object):
    """Jenkins REST API data encoding the state of different Jenkins objects

    :param str config_xml:
        Plain text XML of the Jenkins object, typically loaded from the
        config.xml API endpoint
    """
    def __init__(self, config_xml):
        self._root = ElementTree.fromstring(config_xml)
        self._log = logging.getLogger(__name__)

    def derived_object(self, url):
        """Instantiates the plugin for the root node of the contained XML

        :param str url:
            URL of the REST API endpoint for the object to instantiate
        :returns:
            PyJen object representing the Jenkins plugin associated with the
            root node of the config xml
        """
        return ConfigXML._init_plugin(self._root, url)

    @property
    def xml(self):
        """Extracts the processed XML for export to a Jenkins job

        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.

        :rtype: :class:`str`
        """
        retval = ElementTree.tostring(self._root, "UTF-8")
        return retval.decode("utf-8")

    def plugin_name(self, xml_node=None):
        """Gets the name of Jenkins plugin associated with the given XML snippet

        :param xml_node:
            XML root node containing plugin metadata. If not provided the root
            node of the container is used.
        :returns: the plugin name if one is defined, otherwise None
        :rtype: :class:`str`
        """
        if xml_node is None:
            xml_node = self._root

        return ConfigXML._get_plugin_name_from_node(xml_node)

    @staticmethod
    def _get_plugin_name_from_node(xml_node):
        if 'plugin' not in xml_node.attrib:
            return None

        attr = xml_node.attrib['plugin']
        if '@' not in attr:
            raise ValueError('Jenkins plugin attributes are expected to be of '
                             'the form "name@version": ' + attr)

        parts = attr.split('@')

        return parts[0]

    def plugin_class_name(self, xml_node=None):
        """Java class name of plugin associated with the given XML snippet

        :param xml_node:
            XML root node containing plugin metadata. If not provided the root
            node of the container is used.
        :returns:
            the name of the Java class associated with the given XML snippet
        :rtype: :class:`str`
        """
        if xml_node is None:
            xml_node = self._root

        return ConfigXML._get_plugin_class_name_from_node(xml_node)

    @staticmethod
    def _get_plugin_class_name_from_node(xml_node):
        if "class" in xml_node.attrib:
            return xml_node.attrib['class']
        else:
            return xml_node.tag

    def plugin_version(self, xml_node=None):
        """version of a Jenkins plugin associated with a specific XML node

        :param xml_node:
            XML root node containing plugin metadata. If not provided the root
            node of the container is used.
        :returns: the plugin version, or None if no plugin metadata found
        :rtype: :class:`str`
        """
        if xml_node is None:
            xml_node = self._root
        ConfigXML._get_plugin_version_from_node(xml_node)

    @staticmethod
    def _get_plugin_version_from_node(xml_node):
        if 'plugin' not in xml_node.attrib:
            return None

        attr = xml_node.attrib['plugin']
        if '@' not in attr:
            raise ValueError('Jenkins plugin attributes are expected to be of '
                             'the form "name@version": ' + attr)

        parts = attr.split('@')
        return parts[1]

    @staticmethod
    def _init_plugin(xml_node, obj_url=None):
        """Instantiates a PyJen plugin that wraps a particular Jenkins plugin

        Plugins are defined by an XML node with attributes describing the
        plugin associated with the XML and 0 or more child elements containing
        the parameters used by the plugin. The XML representation of a plugin
        is expected to conform to one of the following patterns:

        * <plugins.MultiJobProject plugin="jenkins-multijob-plugin@1.20">
        * <logRotator class="hudson.tasks.LogRotator">
        * <hudson.model.ListView>

        The first example defines the "friendly" name of the plugin and it's
        associated version number using the pattern "plugin_name@version".
        The second example stores the Java class name associated with the
        Jenkins plugin itself. The last example illustrates how some of the
        built-in types are defined by naming the root tag with the full
        Java class name, which appears to be analogous to the 'class'
        attribute from example 2.

        :param xml_node:
            Root node of the XML subtree representing the plugin to be created
        :param str obj_url:
            URL of the REST API endpoint for the plugin. Only needed for
            plugins that extend default jenkins objects like jobs, views and
            the like.
        :returns:
            Instantiated PyJen object encapsulating the Jenkins plugin
            associated with the given XML
        """
        entry_point_name = \
            ConfigXML._get_plugin_name_from_node(xml_node) or \
            ConfigXML._get_plugin_class_name_from_node(xml_node)
        if entry_point_name is None:
            raise Exception("Parsing error: no valid Jenkins plugin name "
                            "could be parsed from provided XML")

        plugin_class = ConfigXML.find_plugin(entry_point_name)

        if obj_url:
            return plugin_class(obj_url)
        else:
            return plugin_class(xml_node)

    @staticmethod
    def get_installed_plugins():
        """Gets a list of PyJen plugin names installed on the system

        :rtype: :class:`list`
        """
        retval = []
        for entry_point in iter_entry_points(group='pyjen.plugins', name=None):
            retval.append(entry_point.name)
        return retval

    @staticmethod
    def find_plugin(plugin_name):
        """Locates the PyJen class associated with a given Jenkins plugin

        raises a PluginNotSupportedError if no plugin with the given name is
        found

        :param str plugin_name:
            the full name of the Jenkins plugin to find the analogous PyJen
            plugin for
        :returns:
            reference to the PyJen plugin class for the given Jenkins plugin
        """
        supported_plugins = []
        for entry_point in iter_entry_points(
                group='pyjen.plugins', name=plugin_name):
            supported_plugins.append(entry_point.load())

        if len(supported_plugins) == 0:
            raise PluginNotSupportedError("Plugin not supported: " +
                                          plugin_name, plugin_name)

        if len(supported_plugins) > 1:
            tmp_log = logging.getLogger(__name__)
            tmp_log.warning("multiple plugins detected for specified Jenkins"
                            " object: %s. Using first match.", plugin_name)

        return supported_plugins[0]

if __name__ == "__main__":  # pragma: no cover
    # print a list of all installed PyJen plugins
    # plugins = PluginAPI.get_installed_plugins()
    # for p in plugins:
    #       print (p)
    pass
