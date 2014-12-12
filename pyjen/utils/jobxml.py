"""Abstractions for managing the raw config.xml for a Jenkins job"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.pluginapi import get_plugins, PluginXML
from pyjen.exceptions import PluginNotSupportedError
import logging

log = logging.getLogger(__name__)


class JobXML(object):
    """ Wrapper around the config.xml for a Jenkins job
    
    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
     
    """
    def __init__(self, xml):
        """
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        
        self._root = ElementTree.fromstring(xml)

        assert self._root.tag == "project"

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace
        
        If the job is not currently using a custom workspace this method will do nothing
        """
        node = self._root.find('customWorkspace')
        
        if node is not None:
            self._root.remove(node)

    @property
    def custom_workspace(self):
        """Gets the local path for the custom workspace associated with this job

        :returns: the local path for the custom workspace associated with this job
        :rtype: :class:`str`
        """
        node = self._root.find('customWorkspace')
        if node is None:
            return ""
        return node.text

    @custom_workspace.setter
    def custom_workspace(self, path):
        """Defines a new or modified custom workspace for a job

        If the job already has a custom workspace it will be replaced with the given path
        If not then a new custom workspace will be created with the given path

        :param str path: path of the new or modified custom workspace
        """
        node = self._root.find('customWorkspace')

        if node is None:
            node = ElementTree.SubElement(self._root, 'customWorkspace')

        node.text = path

    @property
    def assigned_node(self):
        """Gets the build agent label this job is associated with

        :returns: the build agent label this job is associated with
        :rtype: :class:`str`
        """
        node = self._root.find("assignedNode")
        if node is None:
            return ""
        return node.text

    @assigned_node.setter
    def assigned_node(self, node_label):
        """Sets the build agent label this job is associated with

        :param str node_label: the new build agent label to associate with this job
        """
        node = self._root.find('assignedNode')

        if node is None:
            node = ElementTree.SubElement(self._root, 'assignedNode')

        node.text = node_label

    @property
    def XML(self):
        """Extracts the processed XML for export to a Jenkins job
        
        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.
        
        :rtype: :class:`str`
        """
        retval = ElementTree.tostring(self._root, "UTF-8")
        return retval.decode("utf-8")

    @property
    def scm(self):
        """Retrieves the appropriate plugin for the SCM portion of a job
        
        Detects which source code management tool is being used by this
        job, locates the appropriate plugin for that tool, and returns
        an instance of the wrapper for that plugin pre-configured with
        the settings found in the relevant XML subtree.
        
        :returns: 
            One of any number of plugin objects responsible for providing
            extensions to the source code management portion of a job
        
            Examples: :class:`~pyjen.plugins.subversion.Subversion`
        
        :rtype: :class:`~.pluginapi.PluginXML`
        """
        node = self._root.find('scm')
        xml = ElementTree.tostring(node)

        pluginxml = PluginXML(xml)
        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                return plugin(node)

        raise PluginNotSupportedError("Job XML plugin {0} not found".format(pluginxml.get_class_name()),
                                      pluginxml.get_class_name())

    @property
    def properties(self):
        """Gets a list of 0 or more Jenkins properties associated with this job

        :returns: a list of customizable properties associated with this job
        :rtype: :class:`list` of property plugins supported by this job
        """
        retval = []
        properties_node = self._root.find('properties')
        for property in properties_node:
            pluginxml = PluginXML(ElementTree.tostring(property))
            found_plugin = False
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    retval.append(plugin(property))
                    found_plugin = True
                    break

            if not found_plugin:
                log.warning("Unsupported job 'property' plugin: " + pluginxml.get_class_name())
        return retval

    @property
    def publishers(self):
        """Gets a list of 0 or more post-build publisher objects associated with this job

        :returns: a list of post-build publishers associated with this job
        :rtype: :class:`list` of publisher plugins supported by this job
        """
        retval = []
        publishers_node = self._root.find('publishers')
        for publisher in publishers_node:
            pluginxml = PluginXML(ElementTree.tostring(publisher))
            found_plugin = False
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    retval.append(plugin(publisher))
                    found_plugin = True
                    break

            if not found_plugin:
                log.warning("Unsupported job 'publisher' plugin: " + pluginxml.get_class_name())
        return retval

    @property
    def builders(self):
        """Gets a list of 0 or more build operations associated with this job

        :returns: a list of build operations associated with this job
        :rtype: :class:`list` of builder plugins used by this job
        """
        retval = []
        builders_node = self._root.find('builders')
        for builder in builders_node:
            pluginxml = PluginXML(ElementTree.tostring(builder))
            found_plugin = False
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    retval.append(plugin(builder))
                    found_plugin = True
                    break

            if not found_plugin:
                log.warning("Unsupported job 'builder' plugin: " + pluginxml.get_class_name())

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
