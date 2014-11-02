from pyjen.plugins.pluginbase import pluginbase
from pyjen.job import Job

class maven_plugin(Job):
    """Maven view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(maven_plugin, self).__init__(controller, jenkins_master)

    @staticmethod
    def template_config_xml():
        xml = """<maven2-moduleset plugin="maven-plugin@2.6">
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <properties/>
        <scm class="hudson.scm.NullSCM"/>
        <canRoam>true</canRoam>
        <disabled>false</disabled>
        <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
        <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
        <triggers/>
        <concurrentBuild>false</concurrentBuild>
        <aggregatorStyleBuild>true</aggregatorStyleBuild>
        <incrementalBuild>false</incrementalBuild>
        <ignoreUpstremChanges>false</ignoreUpstremChanges>
        <archivingDisabled>false</archivingDisabled>
        <siteArchivingDisabled>false</siteArchivingDisabled>
        <fingerprintingDisabled>false</fingerprintingDisabled>
        <resolveDependencies>false</resolveDependencies>
        <processPlugins>false</processPlugins>
        <mavenValidationLevel>-1</mavenValidationLevel>
        <runHeadless>false</runHeadless>
        <disableTriggerDownstreamProjects>false</disableTriggerDownstreamProjects>
        <settings class="jenkins.mvn.DefaultSettingsProvider"/>
        <globalSettings class="jenkins.mvn.DefaultGlobalSettingsProvider"/>
        <reporters/>
        <publishers/>
        <buildWrappers/>
        <prebuilders/>
        <postbuilders/>
        <runPostStepsIfResult>
        <name>FAILURE</name>
        <ordinal>2</ordinal>
        <color>RED</color>
        <completeBuild>true</completeBuild>
        </runPostStepsIfResult>
        </maven2-moduleset>"""
        return xml

if __name__ == "__main__": # pragma: no cover
    pass
