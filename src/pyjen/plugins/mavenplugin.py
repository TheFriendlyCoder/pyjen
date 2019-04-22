"""Primitives that operate on Jenkins jobs of type 'Maven'"""
from pyjen.job import Job


class MavenPlugin(Job):
    """Custom Maven job type"""

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def template_config_xml():
        """XML configuration template to when instantiating jobs of this type

        :returns:
            a basic XML configuration template for use when instantiating
            jobs of this type
        :rtype: :class:`str`
        """
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

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "mavenplugin"


PluginClass = MavenPlugin


if __name__ == "__main__":  # pragma: no cover
    pass
