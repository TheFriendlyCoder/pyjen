"""Primitives for operating on Jenkins post-build publisher of type Parameterized Build Trigger"""
import logging
import xml.etree.ElementTree as ElementTree


class BuildTriggerConfig(object):
    """Abstraction around a basic parameterized build trigger"""
    def __init__(self, node):
        """:param node: configuration node loaded from the Jenkins API for this object"""
        self._root = node
        self._log = logging.getLogger(__name__)

    @property
    def job_names(self):
        """Gets a list of names of jobs triggered by this one

        :returns: list of job names
        :rtype: :class:`list` of :class:`str`
        """
        projects_node = self._root.find('projects')
        self._log.info(projects_node.text)
        retval = projects_node.text.split(",")

        # To simplify post-processing, lets make sure to exclude any superfluous white space from the list items
        return [i.lstrip().rstrip() for i in retval]

    @job_names.setter
    def job_names(self, triggered_jobs):
        node = self._root.find('projects')

        if node is None:
            node = ElementTree.SubElement(self._root, 'projects')

        node.text = ",".join(triggered_jobs)


class ParameterizedBuildTrigger:
    """SCM plugin for Jobs with no source control configurations"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def triggers(self):
        """Gets the list of trigger operations defined for this instance of the plugin

        :rtype: :class:`list` of :class:`BuildTriggerConfig` objects
        """
        retval = []
        configs_node = self._root.find('configs')
        for config in configs_node:
            assert config.tag == "hudson.plugins.parameterizedtrigger.BuildTriggerConfig"
            retval.append(BuildTriggerConfig(config))
        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
