"""Primitives that manage Jenkins job of type 'MultiJob'"""
from pyjen.job import Job


class MultiJob(Job):
    """Custom job type provided by the jenkins-multijob-plugin plugin

    https://plugins.jenkins.io/jenkins-multijob-plugin
    """
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "com.tikal.jenkins.plugins.multijob.MultiJobProject"

    @staticmethod
    def template_config_xml():
        """Gets XML for a default implementation of this job type

        :rtype: :class:`str`
        """
        return """
<com.tikal.jenkins.plugins.multijob.MultiJobProject>
    <description/>
    <keepDependencies>false</keepDependencies>
    <properties>
        <hudson.plugins.buildblocker.BuildBlockerProperty>
            <useBuildBlocker>false</useBuildBlocker>
            <blockLevel>GLOBAL</blockLevel>
            <scanQueueFor>DISABLED</scanQueueFor>
            <blockingJobs/>
        </hudson.plugins.buildblocker.BuildBlockerProperty>
    </properties>
    <scm class="hudson.scm.NullSCM"/>
    <canRoam>true</canRoam>
    <disabled>false</disabled>
    <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
    <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
    <triggers/>
    <concurrentBuild>false</concurrentBuild>
    <builders/>
    <publishers/>
    <buildWrappers/>
    <pollSubjobs>false</pollSubjobs>
    </com.tikal.jenkins.plugins.multijob.MultiJobProject>"""


PluginClass = MultiJob

if __name__ == "__main__":  # pragma: no cover
    pass
