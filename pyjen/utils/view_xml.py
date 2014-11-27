"""Abstractions for managing the raw config.xml for a Jenkins view"""
import xml.etree.ElementTree as ElementTree


class view_xml(object):
    def __init__(self, xml):
        """Constructor
        
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        
        self._root = ElementTree.fromstring(xml)

    def get_xml(self):
        """Extracts the processed XML for export to a Jenkins job

        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.

        :rtype: :func:`str`
        """
        retval = ElementTree.tostring(self._root, "UTF-8")
        return retval.decode("utf-8")

    def rename(self, new_name):
        """Changes the name of the view

        :param str new_name: The new name for the view
        """
        node = self._root.find('name')
        node.text = new_name


if __name__ == "__main__":  # pragma: no cover
    pass
