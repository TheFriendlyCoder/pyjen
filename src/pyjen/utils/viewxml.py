"""Abstractions for managing the raw config.xml for a Jenkins view"""
import logging
import xml.etree.ElementTree as ElementTree


class ViewXML(object):
    """Wrapper around the config.xml for a Jenkins view

    Loaded from the ./view/config.xml REST API endpoint for any arbitrary
    Jenkins view.

    :param str config_xml:
        Raw XML character string extracted from a Jenkins view.
    """
    def __init__(self, config_xml):
        super(ViewXML, self).__init__()
        self._root = ElementTree.fromstring(config_xml)
        self._log = logging.getLogger(__name__)

    def __str__(self):
        """String representation of the configuration XML"""
        return self.xml

    @property
    def xml(self):
        """Raw XML in plain-text format

        :rtype: :class:`str`
        """
        return ElementTree.tostring(self._root).decode("utf-8")

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
