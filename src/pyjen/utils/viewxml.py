"""Abstractions for managing the raw config.xml for a Jenkins view"""
import logging
import xml.etree.ElementTree as ElementTree


class ViewXML(object):
    """Wrapper around the config.xml for a Jenkins view

    Loaded from the ./view/config.xml REST API endpoint for any arbitrary
    Jenkins view.

    :param api:
        Rest API for the Jenkins XML configuration managed by this object
    """

    def __init__(self, api):
        super(ViewXML, self).__init__()
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

    def rename(self, new_name):
        """Changes the name of the view

        :param str new_name: The new name for the view
        """
        node = self._root.find('name')
        node.text = new_name


if __name__ == "__main__":  # pragma: no cover
    pass
