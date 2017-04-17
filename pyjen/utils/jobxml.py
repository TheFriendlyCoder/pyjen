"""Abstractions for managing the raw config.xml for a Jenkins job"""
import logging
import xml.etree.ElementTree as ElementTree
from pyjen.exceptions import PluginNotSupportedError
from pyjen.utils.configxml import ConfigXML


class JobXML(ConfigXML):
    """ Wrapper around the config.xml for a Jenkins job

    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
    """
    def __init__(self, xml):
        """
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        super(JobXML, self).__init__(xml)
        assert self._root.tag == "project"
        self._log = logging.getLogger(__name__)

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

        :rtype: :class:`~.pluginapi.PluginBase`
        """
        node = self._root.find('scm')
        plugin = self._init_plugin(node)
        if plugin is not None:
            return plugin

        raise PluginNotSupportedError("SCM XML plugin not found", "scm")

    @property
    def properties(self):
        """Gets a list of 0 or more Jenkins properties associated with this job

        :returns: a list of customizable properties associated with this job
        :rtype: :class:`list` of property plugins supported by this job
        """
        retval = []
        nodes = self._root.find('properties')
        for node in nodes:
            plugin = self._init_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Unsupported job 'property' plugin.")
        return retval

    @property
    def publishers(self):
        """Gets a list of 0 or more post-build publisher objects associated with this job

        :returns: a list of post-build publishers associated with this job
        :rtype: :class:`list` of publisher plugins supported by this job
        """
        retval = []
        nodes = self._root.find('publishers')
        for node in nodes:
            plugin = self._init_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Unsupported job 'publisher' plugin")
        return retval

    @property
    def builders(self):
        """Gets a list of 0 or more build operations associated with this job

        :returns: a list of build operations associated with this job
        :rtype: :class:`list` of builder plugins used by this job
        """
        retval = []
        nodes = self._root.find('builders')
        for node in nodes:
            plugin = self._init_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Unsupported job 'builder' plugin")

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
