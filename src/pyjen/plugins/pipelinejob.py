"""Primitives that manage Jenkins job of type 'Freestyle'"""
from pyjen.job import Job
import xml.etree.ElementTree as ElementTree
from pyjen.utils.jobxml import JobXML
from pyjen.utils.plugin_api import find_plugin
from pyjen.exceptions import PluginNotSupportedError


class PipelineJob(Job):
    """Jenkins job of type 'freestyle'

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(PipelineJob, self).__init__(api)

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "org.jenkinsci.plugins.workflow.job.WorkflowJob"

    @staticmethod
    def template_config_xml():
        return """<flow-definition plugin="workflow-job@2.32">
<description/>
<keepDependencies>false</keepDependencies>
<properties/>
<definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.64">
<script/>
<sandbox>true</sandbox>
</definition>
<triggers/>
<disabled>false</disabled>
</flow-definition>"""

    def scm_definition(self, scm, script_path="Jenkinsfile", lightweight=True):
        """Defines the Pipeline groovy script used by this job from files
        stored in a source code repository

        :param scm:
            PyJen object defining the source code repository to use
        :param str script_path:
            Path within the repository where the groovy script to be run
            is found. Defaults to 'Jenkinsfile' in the root folder
        :param bool lightweight:
            Set to True to have the build only check out the Jenkinsfile and
            no other file from the repository. Set to False to have the build
            check out the entire repository before running the Jenkinsfile.
            Defaults to True
        """
        jobxml = PipelineXML(self.config_xml)
        jobxml.scm_definition(scm, script_path, lightweight)
        self.config_xml = jobxml.xml

    def script_definition(self, script, sandbox=True):
        """Defines the pipeline build using an inline groovy script

        :param str script:
            Raw Groovy script defining the build process
        :param bool sandbox:
            indicates whether the Groovy script can run in the safer 'sandbox'
            environment. Defaults to True.
        """
        jobxml = PipelineXML(self.config_xml)
        jobxml.script_definition(script, sandbox)
        self.config_xml = jobxml.xml

    @property
    def script(self):
        """Gets the groovy script defining this build

        :rtype: :class:`str`
        """
        jobxml = PipelineXML(self.config_xml)
        return jobxml.script

    @property
    def scm(self):
        """Gets the source code repo where the job config is defined"""
        jobxml = PipelineXML(self.config_xml)
        return jobxml.scm


class PipelineXML(JobXML):
    def scm_definition(self, scm, script_path, lightweight):
        """Defines the Pipeline groovy script used by this job from files
        stored in a source code repository

        :param scm:
            PyJen object defining the source code repository to use
        :param str script_path:
            Path within the repository where the groovy script to be run
            is found.
        :param bool lightweight:
            Set to True to have the build only check out the Jenkinsfile and
            no other file from the repository. Set to False to have the build
            check out the entire repository before running the Jenkinsfile.
        """
        definition_node = ElementTree.Element("definition")
        definition_node.attrib["class"] = "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition"
        definition_node.attrib["plugin"] = "workflow-cps"
        definition_node.append(scm.node)

        script_node = ElementTree.Element("scriptPath")
        script_node.text = script_path
        definition_node.append(script_node)

        lightweight_node = ElementTree.Element("lightweight")
        lightweight_node.text = str(lightweight)
        definition_node.append(lightweight_node)

        if self._root.find("definition"):
            self._root.remove(self._root.find("definition"))
        self._root.append(definition_node)

    def script_definition(self, script, sandbox):
        """Defines the pipeline build using an inline groovy script

        :param str script:
            Raw Groovy script defining the build process
        :param bool sandbox:
            indicates whether the Groovy script can run in the safer 'sandbox'
            environment.
        """
        definition_node = ElementTree.Element("definition")
        definition_node.attrib["class"] = "org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition"
        definition_node.attrib["plugin"] = "workflow-cps"

        script_node = ElementTree.Element("script")
        script_node.text = script
        definition_node.append(script_node)

        sandbox_node = ElementTree.Element("sandbox")
        sandbox_node.text = str(sandbox)
        definition_node.append(sandbox_node)

        if self._root.find("definition"):
            self._root.remove(self._root.find("definition"))
        self._root.append(definition_node)

    @property
    def script(self):
        """Gets the groovy script that defines the build process for this job"""
        definition_node = self._root.find("definition")
        if "CpsFlowDefinition" not in definition_node.attrib["class"]:
            return ""
        script_node = definition_node.find("script")
        assert script_node is not None
        return script_node.text

    @property
    def scm(self):
        """Gets the source code repo where the build script is located"""
        definition_node = self._root.find("definition")
        if "CpsScmFlowDefinition" not in definition_node.attrib["class"]:
            return None
        scm_node = definition_node.find("scm")
        assert scm_node is not None
        assert "class" in scm_node.attrib
        plugin_name = scm_node.attrib["class"]
        plugin = find_plugin(plugin_name)
        if plugin is None:
            raise PluginNotSupportedError(
                "PyJen has no plugin installed for Jenkins plugin " +
                plugin_name)
        return plugin(scm_node)

PluginClass = PipelineJob

if __name__ == "__main__":  # pragma: no cover
    pass




