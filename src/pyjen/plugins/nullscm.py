"""SCM properties of Jenkins jobs with no source control configuration"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class NullSCM(XMLPlugin):
    """SCM plugin for Jobs with no source control configurations"""

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.scm.NullSCM"

    @classmethod
    def instantiate(cls):
        """Factory method used to construct instances of this class

        :rtype: :class:`NullSCM`
        """
        root_node = ElementTree.fromstring('<scm class="hudson.scm.NullSCM"/>')
        return cls(root_node)


PluginClass = NullSCM

if __name__ == "__main__":  # pragma: no cover
    pass
