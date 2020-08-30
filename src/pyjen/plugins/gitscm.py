"""SCM properties for jobs which pull sources from a Git repository"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class GitSCM(XMLPlugin):
    """SCM properties for jobs which pull sources from a Git repository"""

    @property
    def url(self):
        """str: the repository URL for the git config"""
        branches_node = self._root.find("userRemoteConfigs")
        remotes_node = branches_node.find("hudson.plugins.git.UserRemoteConfig")
        url_node = remotes_node.find("url")
        return url_node.text

    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.plugins.git.GitSCM"

    @classmethod
    def instantiate(cls, repository_url):
        """Factory method for creating a new Git SCM code block

        Args:
            repository_url (str):
                URI of the repository to check out during the build

        Returns:
            GitSCM:
                reference to the newly instantiated object
        """
        default_xml = """
<scm class="hudson.plugins.git.GitSCM">
    <configVersion>2</configVersion>
    <branches>
        <hudson.plugins.git.BranchSpec>
            <name>*/master</name>
        </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <submoduleCfg class="list"/>
    <extensions/>
</scm>"""
        root_node = ElementTree.fromstring(default_xml)

        remotes = ElementTree.SubElement(root_node, "userRemoteConfigs")
        config = ElementTree.SubElement(
            remotes, "hudson.plugins.git.UserRemoteConfig")
        url = ElementTree.SubElement(config, "url")

        url.text = repository_url

        return cls(root_node)


PluginClass = GitSCM

if __name__ == "__main__":  # pragma: no cover
    pass
