"""Abstractions for managing the raw config.xml for a Jenkins job"""
import logging
import xml.etree.ElementTree as ElementTree
from pyjen.utils.plugin_api import find_plugin


class JobXML(object):
    """ Wrapper around the config.xml for a Jenkins job

    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"

    :param api:
        Rest API for the Jenkins XML configuration managed by this object
    """
    def __init__(self, api):
        super(JobXML, self).__init__()
        self._api = api
        self._log = logging.getLogger(__name__)
        self._cache = None

    def __str__(self):
        """String representation of the configuration XML"""
        return self.xml

    @property
    def _root(self):
        """Gets the decoded root node from the config xml"""
        if self._cache is not None:
            return self._cache
        text = self._api.get_text("/config.xml")
        self._cache = ElementTree.fromstring(text)
        return self._cache

    def update(self):
        """Posts all changes made to the object back to Jenkins"""
        args = {'data': self.xml, 'headers': {'Content-Type': 'text/xml'}}
        self._api.post(self._api.url + "config.xml", args)

    @property
    def xml(self):
        """Raw XML in plain-text format

        :rtype: :class:`str`
        """
        return ElementTree.tostring(self._root).decode("utf-8")

    @xml.setter
    def xml(self, value):
        self._cache = ElementTree.fromstring(value)
        self.update()

    @property
    def plugin_name(self):
        """Gets the name of the Jenkins plugin associated with this view

        :rtype: :class:`str`
        """
        return self._root.tag

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
