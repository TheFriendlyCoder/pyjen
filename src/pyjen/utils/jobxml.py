"""Abstractions for managing the raw config.xml for a Jenkins job"""
import logging
import xml.etree.ElementTree as ElementTree
from pyjen.utils.plugin_api import find_plugin


class JobXML(object):
    """ Wrapper around the config.xml for a Jenkins job

    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"

    :param str config_xml:
        Raw XML character string extracted from a Jenkins job.
    """
    def __init__(self, api):
        super(JobXML, self).__init__()
        self._api = api
        self._log = logging.getLogger(__name__)
        self._cache = None

    @property
    def _root(self):
        """Gets the decoded root node from the config xml"""
        if self._cache is not None:
            return self._cache
        text = self._api.get_text("/config.xml")
        self._cache = ElementTree.fromstring(text)
        return self._cache

    def __str__(self):
        """String representation of the configuration XML"""
        return self.xml

    def update(self):
        """Posts all changes made to the object back to Jenkins"""
        args = {'data': self.xml, 'headers': {'Content-Type': 'text/xml'}}
        self._api.post(self._api.url + "config.xml", args)

    @property
    def quiet_period(self):
        """Gets the delay, in seconds, this job waits in queue before running
        a build

        May return None if no custom quiet period is defined. At the time of
        this writing the default value is 5 seconds however this may change
        over time.

        :rtype: :class:`int`
        """
        node = self._root.find("quietPeriod")
        if node is None:
            return None
        return int(node.text)

    @quiet_period.setter
    def quiet_period(self, value):
        """Changes the quiet period

        :param int value: time, in seconds, to set the quiet period to
        """
        node = self._root.find("quietPeriod")
        if node is None:
            node = ElementTree.SubElement(self._root, 'quietPeriod')
        node.text = str(value)

    @property
    def xml(self):
        """Raw XML in plain-text format

        :rtype: :class:`str`
        """
        return ElementTree.tostring(self._root).decode("utf-8")

    @xml.setter
    def xml(self, new_xml):
        """Updates the job config from some new, statically defined XML source

        :param str new_xml:
            raw XML config data to be uploaded
        """
        args = {'data': new_xml, 'headers': {'Content-Type': 'text/xml'}}
        self._api.post(self._api.url + "config.xml", args)
        self._cache = ElementTree.fromstring(new_xml)

    @property
    def plugin_name(self):
        """Gets the name of the Jenkins plugin associated with this view

        :rtype: :class:`str`
        """
        return self._root.tag

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace

        If the job is not currently using a custom workspace this method will
        do nothing
        """
        node = self._root.find('customWorkspace')

        if node is not None:
            self._root.remove(node)

    @property
    def custom_workspace(self):
        """Gets the local path for the custom workspace associated with this job

        :returns:
            the local path for the custom workspace associated with this job
        :rtype: :class:`str`
        """
        node = self._root.find('customWorkspace')
        if node is None:
            return ""
        return node.text

    @custom_workspace.setter
    def custom_workspace(self, path):
        """Defines a new or modified custom workspace for a job

        If the job already has a custom workspace it will be replaced with the
        given path. If not then a new custom workspace will be created with the
        given path

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

        :param str node_label:
        the new build agent label to associate with this job
        """
        node = self._root.find('assignedNode')

        if node is None:
            node = ElementTree.SubElement(self._root, 'assignedNode')

        node.text = node_label

    @property
    def properties(self):
        """Gets a list of 0 or more Jenkins properties associated with this job

        :returns: a list of customizable properties associated with this job
        :rtype: :class:`list` of property plugins supported by this job
        """
        retval = list()
        nodes = self._root.find('properties')
        for node in nodes:
            plugin = find_plugin(node.tag)
            if plugin is not None:
                temp = plugin(node)
                temp.parent = self
                retval.append(temp)
            else:
                self._log.warning(
                    "Unsupported job 'property' plugin: %s", node.tag)
        return retval

    def add_property(self, prop):
        """Adds a new job property to the configuration

        :param prop:
            PyJen plugin associated with the job property to add
        """
        props_node = self._root.find('properties')
        props_node.append(prop.node)
        prop.parent = self


if __name__ == "__main__":  # pragma: no cover
    pass
