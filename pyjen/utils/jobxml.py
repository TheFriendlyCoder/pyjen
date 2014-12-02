"""Abstractions for managing the raw config.xml for a Jenkins job"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.pluginapi import get_plugins, PluginXML
from pyjen.exceptions import PluginNotSupportedError


class JobXML(object):
    """ Wrapper around the config.xml for a Jenkins job
    
    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
     
    """
    def __init__(self, xml):
        """Constructor
        
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        
        self.__root = ElementTree.fromstring(xml)

        assert (self.__root.tag == "project")

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace
        
        If the job is not currently using a custom workspace this method will do nothing
        """
    
        Node = self.__root.find('customWorkspace')
        
        if Node != None:
            self.__root.remove(Node)

    @property
    def custom_workspace(self):
        """Gets the local path for the custom workspace associated with this job

        :returns: the local path for the custom workspace associated with this job
        :rtype: :func:`str`
        """
        Node = self.__root.find('customWorkspace')
        if Node is None:
            return ""
        return Node.text

    @custom_workspace.setter
    def custom_workspace(self, path):
        """Defines a new or modified custom workspace for a job

        If the job already has a custom workspace it will be replaced with the given path
        If not then a new custom workspace will be created with the given path

        :param str path: path of the new or modified custom workspace
        """
        Node = self.__root.find('customWorkspace')

        if Node is None:
            Node = ElementTree.SubElement(self.__root, 'customWorkspace')

        Node.text = path

    @property
    def assigned_node(self):
        """Gets the build agent label this job is associated with
        :returns: the build agent label this job is associated with
        :rtype: :func:`str`
        """
        Node = self.__root.find("assignedNode")
        if Node is None:
            return ""
        return Node.text

    @assigned_node.setter
    def assigned_node(self, node_label):
        """Sets the build agent label this job is associated with
        :param str node_label: the new build agent label to associate with this job
        """
        Node = self.__root.find('assignedNode')

        if Node is None:
            Node = ElementTree.SubElement(self.__root, 'assignedNode')

        Node.text = node_label

    @property
    def XML(self):
        """Extracts the processed XML for export to a Jenkins job
        
        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.
        
        :rtype: :func:`str`
        """
        retval = ElementTree.tostring(self.__root, "UTF-8")
        return retval.decode("utf-8")

    @property
    def scm(self):
        """Retrieves the appropriate plugin for the SCM portion of a job
        
        Detects which source code management tool is being used by this
        job, locates the appropriate plugin for that tool, and returns
        an instance of the wrapper for that plugin pre-configured with
        the settings found in the relevant XML subtree.
        
        :returns: 
            One of any number of plugin objects responsible for providing
            extensions to the source code management portion of a job
        
            Examples: :py:mod:`pyjen.plugins.Subversion`
        
        :rtype: :py:mod:`pyjen.plugins.PluginXML`
        """
        Node = self.__root.find('scm')
        xml = ElementTree.tostring(Node)

        pluginxml = PluginXML(xml)
        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                return plugin(Node)

        raise PluginNotSupportedError("Job XML plugin {0} not found".format(pluginxml.get_class_name()), pluginxml.get_class_name())

    @property
    def properties(self):
        """Gets a list of 0 or more Jenkins properties associated with this job"""
        retval = []
        properties_node = self.__root.find('properties')
        for property in properties_node:
            pluginxml = PluginXML(ElementTree.tostring(property))
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    retval.append(plugin(property))
            #TODO: Report missing plugins here as warnings or non-blocking errors
        return retval


if __name__ == "__main__":  # pragma: no cover
    pass

    xml = r"""<?xml version="1.0" encoding="UTF-8"?><project>
  <actions/>
  <description/>
  <logRotator class="hudson.tasks.LogRotator">
    <daysToKeep>-1</daysToKeep>
    <numToKeep>30</numToKeep>
    <artifactDaysToKeep>-1</artifactDaysToKeep>
    <artifactNumToKeep>-1</artifactNumToKeep>
  </logRotator>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.plugins.buildblocker.BuildBlockerProperty plugin="build-blocker-plugin@1.4.1">
      <useBuildBlocker>true</useBuildBlocker>
      <blockingJobs>unified-trunk-bdb-.*-build-32
unified-trunk-bdb-.*-package-32
unified-9.9.x-easyview-package-32</blockingJobs>
    </hudson.plugins.buildblocker.BuildBlockerProperty>
    <com.suryagaddipati.jenkins.SlaveUtilizationProperty plugin="slave-utilization-plugin@1.5">
      <needsExclusiveAccessToNode>false</needsExclusiveAccessToNode>
      <singleInstancePerSlave>false</singleInstancePerSlave>
      <salveUtilizationPercentage>0</salveUtilizationPercentage>
    </com.suryagaddipati.jenkins.SlaveUtilizationProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.ChoiceParameterDefinition>
          <name>TypeOfBuild</name>
          <description>Specifies whether to do an incremental or clean build. Default behavior performs incremental build.</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>build</string>
              <string>rebuild</string>
              <string>clean</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
    <hudson.plugins.throttleconcurrents.ThrottleJobProperty plugin="throttle-concurrents@1.8.2">
      <maxConcurrentPerNode>0</maxConcurrentPerNode>
      <maxConcurrentTotal>0</maxConcurrentTotal>
      <categories/>
      <throttleEnabled>false</throttleEnabled>
      <throttleOption>project</throttleOption>
      <configVersion>1</configVersion>
    </hudson.plugins.throttleconcurrents.ThrottleJobProperty>
  </properties>
  <scm class="hudson.scm.SubversionSCM" plugin="subversion@2.3">
    <locations>
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>http://svn.caris.priv/repos/auth/development/unified/trunk/bathy/applications</remote>
        <credentialsId/>
        <local>.</local>
        <depthOption>infinity</depthOption>
        <ignoreExternalsOption>false</ignoreExternalsOption>
      </hudson.scm.SubversionSCM_-ModuleLocation>
    </locations>
    <excludedRegions/>
    <includedRegions/>
    <excludedUsers/>
    <excludedRevprop/>
    <excludedCommitMessages/>
    <workspaceUpdater class="hudson.scm.subversion.UpdateUpdater"/>
    <ignoreDirPropChanges>false</ignoreDirPropChanges>
    <filterChangelog>false</filterChangelog>
  </scm>
  <quietPeriod>70</quietPeriod>
  <assignedNode>unified_build_boxes_32</assignedNode>
  <canRoam>false</canRoam>
  <disabled>true</disabled>
  <blockBuildWhenDownstreamBuilding>true</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>true</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>* * * * *</spec>
      <ignorePostCommitHooks>false</ignorePostCommitHooks>
    </hudson.triggers.SCMTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <customWorkspace>unified\win32\bathy\applications</customWorkspace>
  <builders>
    <hudson.tasks.BatchFile>
      <command>echo BDB Applications: %SVN_URL% @ %SVN_REVISION% &gt; ../../bdb_apps_env.txt</command>
    </hudson.tasks.BatchFile>
    <hudson.tasks.BatchFile>
      <command>"%VS120COMNTOOLS%..\..\VC\vcvarsall.bat" x86 &amp; msbuild /t:%TypeOfBuild% /p:platform=win32;configuration=release;BUILD_LABEL=%BUILD_ID%</command>
    </hudson.tasks.BatchFile>
  </builders>
  <publishers>
    <hudson.plugins.logparser.LogParserPublisher plugin="log-parser@1.0.8">
      <unstableOnWarning>false</unstableOnWarning>
      <failBuildOnError>false</failBuildOnError>
      <parsingRulesPath>C:\Users\builder\.jenkins\log_parsers\cpp.txt</parsingRulesPath>
    </hudson.plugins.logparser.LogParserPublisher>
    <hudson.plugins.parameterizedtrigger.BuildTrigger plugin="parameterized-trigger@2.24">
      <configs>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
              <properties>IS_CLEAN_BUILD=${IS_CLEAN_BUILD}</properties>
            </hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
          </configs>
          <projects>unified-9.9.x-bdb-editor-package-32,unified-9.9.x-hips-build-32,unified-9.9.x-editor-package-32</projects>
          <condition>SUCCESS</condition>
          <triggerWithNoParameters>true</triggerWithNoParameters>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
      </configs>
    </hudson.plugins.parameterizedtrigger.BuildTrigger>
    <org.jenkins__ci.plugins.flexible__publish.FlexiblePublisher plugin="flexible-publish@0.12">
      <publishers>
        <org.jenkins__ci.plugins.flexible__publish.ConditionalPublisher>
          <condition class="org.jenkins_ci.plugins.run_condition.core.StatusCondition" plugin="run-condition@1.0">
            <worstResult>
              <name>FAILURE</name>
              <ordinal>2</ordinal>
              <color>RED</color>
              <completeBuild>true</completeBuild>
            </worstResult>
            <bestResult>
              <name>FAILURE</name>
              <ordinal>2</ordinal>
              <color>RED</color>
              <completeBuild>true</completeBuild>
            </bestResult>
          </condition>
          <publisher class="hudson.plugins.parameterizedtrigger.TriggerBuilder" plugin="parameterized-trigger@2.24">
            <configs>
              <hudson.plugins.parameterizedtrigger.BlockableBuildTriggerConfig>
                <configs>
                  <hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
                    <properties>BUILD_TRIGGER=$JOB_URL
BUILD_TRIGGER_NUM=$BUILD_NUMBER</properties>
                  </hudson.plugins.parameterizedtrigger.PredefinedBuildParameters>
                </configs>
                <projects>build_breakers</projects>
                <condition>ALWAYS</condition>
                <triggerWithNoParameters>false</triggerWithNoParameters>
                <buildAllNodesWithLabel>false</buildAllNodesWithLabel>
              </hudson.plugins.parameterizedtrigger.BlockableBuildTriggerConfig>
            </configs>
          </publisher>
          <runner class="org.jenkins_ci.plugins.run_condition.BuildStepRunner$Fail" plugin="run-condition@1.0"/>
        </org.jenkins__ci.plugins.flexible__publish.ConditionalPublisher>
      </publishers>
    </org.jenkins__ci.plugins.flexible__publish.FlexiblePublisher>
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper plugin="timestamper@1.5.11"/>
    <org.jenkinsci.plugins.buildnamesetter.BuildNameSetter plugin="build-name-setter@1.3">
      <template>${ENV,var="BUILD_ID"}</template>
    </org.jenkinsci.plugins.buildnamesetter.BuildNameSetter>
  </buildWrappers>
</project>"""
    jxml = JobXML(xml)
