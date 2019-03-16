"""Interfaces for interacting with Build Blockers job property plugin"""
import xml.etree.ElementTree as ElementTree


class BuildBlockerProperty(object):
    """Wrapper for Build Blocker job properties

    https://wiki.jenkins-ci.org/display/JENKINS/Build+Blocker+Plugin
    """

    def __init__(self, node):
        """
        :param node:
            ElementTree node initialized with the XML from the Jenkins job
        """
        self._root = node

    @property
    def node(self):
        """Gets the XML node associated with this plugin

        :rtype: :class:`ElementTree.Element`
        """
        return self._root

    @property
    def blockers(self):
        """Gets the list of search criteria for blocking jobs

        :return: list of search criteria for blocking jobs
        :rtype: :class:`list`
        """
        retval = []
        if not self.is_enabled:
            return retval

        temp = self._root.find("blockingJobs").text
        if temp is None:
            return retval

        retval = temp.split()
        return retval

    @blockers.setter
    def blockers(self, new_blockers):
        """Sets the list of search criteria for blocking jobs

        :param list new_blockers: list of search criteria for blocking jobs
        """
        node = self._root.find("blockingJobs")
        if node is None:
            node = ElementTree.SubElement(self._root, 'blockingJobs')
        node.text = "\n".join(new_blockers)

    @property
    def is_enabled(self):
        """Checks to see whether this blockers property is currently enabled

        :returns: True if these blocking jobs are enabled, False if not
        :rtype: :class:`str`
        """
        temp = self._root.find("useBuildBlocker").text
        return temp.lower() == "true"

    def enable(self):
        """Enables this set of build blockers"""
        node = self._root.find("useBuildBlocker")
        if node is None:
            node = ElementTree.SubElement(self._root, 'useBuildBlocker')
        node.text = "true"

    def disable(self):
        """Disables this set of build blockers"""
        node = self._root.find("useBuildBlocker")
        if node is None:
            node = ElementTree.SubElement(self._root, 'useBuildBlocker')
        node.text = "false"

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "buildblocker"


PluginClass = BuildBlockerProperty


if __name__ == "__main__":  # pragma: no cover
    pass
