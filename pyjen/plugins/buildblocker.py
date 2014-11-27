import xml.etree.ElementTree as ElementTree
from pyjen.utils.pluginapi import PluginBase

class BuildBlockerProperty(PluginBase):
    def __init__(self, node):
        """constructor

        :param node: ElementTree node initialized with the XML from the Jenkins job
        """
        self._root = node

    @property
    def blockers(self):
        retval = []
        if not self.is_enabled:
            return retval

        temp = self._root.find("blockingJobs").text
        if temp is None:
            return retval

        retval = temp.split()
        return retval

    def set_blockers(self, new_blockers):
        Node = self._root.find("blockingJobs")
        if Node is None:
            Node = ElementTree.SubElement(self._root, 'blockingJobs')
        Node.text = "\n".join(new_blockers)

    @property
    def is_enabled(self):
        temp = self._root.find("useBuildBlocker").text
        return temp.lower() == "true"

    @property
    def enable(self):
        Node = self._root.find("useBuildBlocker")
        if Node is None:
            Node = ElementTree.SubElement(self._root, 'useBuildBlocker')
        Node.text = "true"

    @property
    def disable(self):
        Node = self._root.find("useBuildBlocker")
        if Node is None:
            Node = ElementTree.SubElement(self._root, 'useBuildBlocker')
        Node.text = "false"

    type = "hudson.plugins.buildblocker.BuildBlockerProperty"