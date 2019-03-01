"""SCM properties of Jenkins jobs with no source control configuration"""


class NullSCM(object):
    """SCM plugin for Jobs with no source control configurations"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert 'class' in self._root.attrib
        assert self._root.attrib['class'] == 'hudson.scm.NullSCM'

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.scm.NullSCM"


PluginClass = NullSCM

if __name__ == "__main__":  # pragma: no cover
    pass
