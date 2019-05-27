"""Primitives that manage Jenkins job of type 'multibranch pipeline'"""
from pyjen.job import Job


class MultibranchPipelineJob(Job):
    """Jenkins job of type 'multibranch pipeline'"""

    @property
    def jobs(self):
        """Gets all branch jobs managed by this multibranch pipeline

        :rtype: :class:`list` of :class:`~.pipelinejob.PipelineJob`
        """
        data = self._api.get_api_data(query_params="depth=0")

        retval = list()
        for j in data["jobs"]:
            retval.append(Job.instantiate(j, self._api))

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return \
            "org.jenkinsci.plugins.workflow.multibranch." \
            "WorkflowMultiBranchProject"

    @staticmethod
    def template_config_xml():
        """Gets config xml data to instantiate a default instance of this job

        :rtype: :class:`str`
        """
        return """
<org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject>
    <actions/>
    <description/>
    <properties>
        <org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
            <dockerLabel/>
            <registry/>
        </org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
    </properties>
    <folderViews class="jenkins.branch.MultiBranchProjectViewHolder">
      <owner 
  class="org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject" 
  reference="../.."/>
    </folderViews>
    <healthMetrics>
        <com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
            <nonRecursive>false</nonRecursive>
        </com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
    </healthMetrics>
    <icon class="jenkins.branch.MetadataActionFolderIcon">
        <owner 
  class="org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject" 
  reference="../.."/>
    </icon>
    <orphanedItemStrategy 
class="com.cloudbees.hudson.plugins.folder.computed.DefaultOrphanedItemStrategy"
>
        <pruneDeadBranches>true</pruneDeadBranches>
        <daysToKeep>-1</daysToKeep>
        <numToKeep>-1</numToKeep>
    </orphanedItemStrategy>
    <triggers/>
    <disabled>false</disabled>
    <sources class="jenkins.branch.MultiBranchProject$BranchSourceList">
        <data/>
        <owner 
  class="org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject" 
  reference="../.."/>
    </sources>
    <factory 
class="org.jenkinsci.plugins.workflow.multibranch.WorkflowBranchProjectFactory">
        <owner 
  class="org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject" 
  reference="../.."/>
        <scriptPath>Jenkinsfile</scriptPath>
    </factory>
</org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject>"""


PluginClass = MultibranchPipelineJob

if __name__ == "__main__":  # pragma: no cover
    pass
