import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class BuildTriggerConfig(XMLPlugin):
    """Abstraction around a basic parameterized build trigger
    """

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.parameterizedtrigger.BuildTriggerConfig"

    @property
    def job_names(self):
        """Gets a list of names of jobs triggered by this one

        :returns: list of job names
        :rtype: :class:`list` of :class:`str`
        """
        projects_node = self._root.find('projects')
        self._log.info(projects_node.text)
        retval = projects_node.text.split(",")

        # To simplify post-processing, lets make sure to exclude any
        # superfluous white space from the list items
        return [i.lstrip().rstrip() for i in retval]

    @job_names.setter
    def job_names(self, triggered_jobs):
        node = self._root.find('projects')

        if node is None:
            node = ElementTree.SubElement(self._root, 'projects')

        node.text = ",".join(triggered_jobs)


PluginClass = BuildTriggerConfig


if __name__ == "__main__":  # pragma: no cover
    pass
