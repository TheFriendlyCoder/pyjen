from pyjen.utils.pluginapi import PluginBase

class NullSCM(PluginBase):
    """Subversion SCM plugin"""

    def __init__(self, node):
        """constructor

        :param node: ElementTree node initialized with the XML from the Jenkins job
        """
        self._root = node

    type = "hudson.scm.NullSCM"