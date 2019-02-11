"""Abstractions for managing the raw config.xml for a Jenkins view"""
from pyjen.utils.configxml import ConfigXML


class ViewXML(ConfigXML):
    """ Wrapper around the config.xml for a Jenkins view

    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
    """
    def __init__(self, xml):
        """
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        super(ViewXML, self).__init__(xml)

    def rename(self, new_name):
        """Changes the name of the view

        :param str new_name: The new name for the view
        """
        node = self._root.find('name')
        node.text = new_name


if __name__ == "__main__":  # pragma: no cover
    pass
