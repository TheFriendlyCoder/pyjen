"""Abstractions for managing the raw config.xml for a Jenkins view"""
import xml.etree.ElementTree as ElementTree


class ViewXML(object):
    """ Wrapper around the config.xml for a Jenkins view

    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
    """
    def __init__(self, xml):
        """
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        self._root = ElementTree.fromstring(xml)

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

    def rename(self, new_name):
        """Changes the name of the view

        :param str new_name: The new name for the view
        """
        node = self._root.find('name')
        node.text = new_name


if __name__ == "__main__":  # pragma: no cover
    pass
