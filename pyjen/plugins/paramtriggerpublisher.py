"""Primitives for operating on Jenkins post-build publisher of type Parameterized Build Trigger"""
from pyjen.utils.pluginapi import PluginBase
import xml.etree.ElementTree as ElementTree
import logging

log = logging.getLogger(__name__)


class BuildTriggerConfig(object):
    def __init__(self, node):
        self._root = node

    @property
    def job_names(self):
        """Gets a list of names of jobs triggered by this one

        :returns: list of job names
        :rtype: :class:`list` of :class:`str`
        """
        projects_node = self._root.find('projects')
        log.info(projects_node.text)
        retval = projects_node.text.split(",")

        # To simplify post-processing, lets make sure to exclude any superfluous white space from the list items
        return [i.lstrip().rstrip() for i in retval]

    @job_names.setter
    def job_names(self, triggered_jobs):
        node = self._root.find('projects')

        if node is None:
            node = ElementTree.SubElement(self._root, 'projects')

        node.text = ",".join(triggered_jobs)


class ParameterizedBuildTrigger(PluginBase):
    """SCM plugin for Jobs with no source control configurations"""
    type = "hudson.plugins.parameterizedtrigger.BuildTrigger"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def triggers(self):
        retval = []
        configs_node = self._root.find('configs')
        for config in configs_node:
            assert config.tag == "hudson.plugins.parameterizedtrigger.BuildTriggerConfig"
            retval.append(BuildTriggerConfig(config))
        return retval

if __name__ == "__main__":  # pragma: no cover
    pass

