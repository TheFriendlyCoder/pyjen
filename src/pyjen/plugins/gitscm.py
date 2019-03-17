"""SCM properties for jobs which pull sources from a Git repository"""
import xml.etree.ElementTree as ElementTree


class GitSCM(object):
    """SCM properties for jobs which pull sources from a Git repository"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def node(self):
        """Gets the XML node associated with this plugin

        :rtype: :class:`ElementTree.Element`
        """
        return self._root

    @property
    def url(self):
        """Gets the repository URL for the git config"""
        branches_node = self._root.find("userRemoteConfigs")
        remotes_node = branches_node.find("hudson.plugins.git.UserRemoteConfig")
        url_node = remotes_node.find("url")
        return url_node.text

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.git.GitSCM"

    @staticmethod
    def create(repository_url):
        """Factory method for creating a new Git SCM code block

        :param str repository_url:
            URI of the repository to check out during the build
        :rtype: :class:`pyjen.plugins.gitscm.GitSCM`
        """
        default_xml = """<scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3">
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
        config = ElementTree.SubElement(remotes, "hudson.plugins.git.UserRemoteConfig")
        url = ElementTree.SubElement(config, "url")

        url.text = repository_url

        return GitSCM(root_node)


PluginClass = GitSCM

if __name__ == "__main__":  # pragma: no cover
    pass
