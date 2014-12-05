"""Primitives for operating on SCM properties of Jenkins jobs with no source control configuration"""
from pyjen.utils.pluginapi import PluginBase


class NullSCM(PluginBase):
    """SCM plugin for Jobs with no source control configurations"""
    type = "hudson.scm.NullSCM"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node


if __name__ == "__main__":  # pragma: no cover
    pass
