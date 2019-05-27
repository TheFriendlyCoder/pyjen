"""Interfaces for interacting with Build Blockers job property plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class BuildBlockerProperty(XMLPlugin):
    """Wrapper for Build Blocker job properties

    https://wiki.jenkins-ci.org/display/JENKINS/Build+Blocker+Plugin
    """
    QUEUE_SCAN_TYPES = ("DISABLED", "ALL", "BUILDABLE")
    LEVEL_TYPES = ("GLOBAL", "NODE")

    @property
    def queue_scan(self):
        """Checks to see whether build blocking scans the build queue or not

        :returns: One of BuildBlockerProperty.QUEUE_SCAN_TYPES
        :rtype: :class:`str`
        """
        retval = self._root.find("scanQueueFor").text
        assert retval in BuildBlockerProperty.QUEUE_SCAN_TYPES
        return retval

    @queue_scan.setter
    def queue_scan(self, value):
        """Sets the type of build queue scanning for the blocking job

        :param str value:
            type of queue scanning to perform
            Must be one of BuildBlockerProperty.QUEUE_SCAN_TYPES
        """
        if value not in BuildBlockerProperty.QUEUE_SCAN_TYPES:
            raise ValueError(
                "Build blocker queue scan may only be one of the following "
                "types: " + ",".join(BuildBlockerProperty.QUEUE_SCAN_TYPES))
        self._root.find("scanQueueFor").text = value
        self.update()

    @property
    def level(self):
        """Gets the scope of the blocked job settings

        :returns: One of BuildBlockerProperty.LEVEL_TYPES
        :rtype: :class:`str`
        """
        retval = self._root.find("blockLevel").text
        assert retval in BuildBlockerProperty.LEVEL_TYPES
        return retval

    @level.setter
    def level(self, value):
        """Sets the scope of the blocked builds

        :param str value:
            scope for this build blocker
            Must be one of BuildBlockerProperty.LEVEL_TYPES
        """
        if value not in BuildBlockerProperty.LEVEL_TYPES:
            raise ValueError(
                "Build blocker scope level may only be one of the following "
                "types: " + ",".join(BuildBlockerProperty.LEVEL_TYPES))
        self._root.find("blockLevel").text = value
        self.update()

    @property
    def blockers(self):
        """Gets the list of search criteria for blocking jobs

        :return: list of search criteria for blocking jobs
        :rtype: :class:`list`
        """
        temp = self._root.find("blockingJobs").text
        return temp.split()

    @blockers.setter
    def blockers(self, patterns):
        """Defines the names or regular expressions for jobs that block
        execution of this job

        :param patterns:
            One or more names or regular expressions for jobs that block the
            execution of this one.
        :type patterns: either :class:`list` or :class:`str`
        """
        node = self._root.find("blockingJobs")
        if isinstance(patterns, str):
            node.text = patterns
        else:
            node.text = "\n".join(patterns)
        self.update()

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
        node.text = "true"
        self.update()

    def disable(self):
        """Disables this set of build blockers"""
        node = self._root.find("useBuildBlocker")
        node.text = "false"
        self.update()

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.buildblocker.BuildBlockerProperty"

    @classmethod
    def instantiate(cls, patterns):
        """Factory method used to instantiate an instance of this plugin

        :param patterns:
            One or more names or regular expressions for jobs that block the
            execution of this one.
        :type patterns: either :class:`list` or :class:`str`
        """
        default_xml = """
<hudson.plugins.buildblocker.BuildBlockerProperty>
    <useBuildBlocker>true</useBuildBlocker>
    <blockLevel>GLOBAL</blockLevel>
    <scanQueueFor>DISABLED</scanQueueFor>
</hudson.plugins.buildblocker.BuildBlockerProperty>"""

        root_node = ElementTree.fromstring(default_xml)
        jobs_node = ElementTree.SubElement(root_node, "blockingJobs")
        if isinstance(patterns, str):
            jobs_node.text = patterns
        else:
            jobs_node.text = " ".join(patterns)
        return cls(root_node)


PluginClass = BuildBlockerProperty


if __name__ == "__main__":  # pragma: no cover
    pass
