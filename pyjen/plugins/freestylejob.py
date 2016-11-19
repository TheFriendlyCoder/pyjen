"""Primitives that manage Jenkins job of type 'Freestyle'"""
from pyjen.job import Job
from pyjen.utils.jobxml import JobXML


class FreestyleJob(Job):
    """Jenkins job of type 'freestyle' """
    type = "project"

    def __init__(self, controller, jenkins_master):
        """
        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master:
            Reference to Jenkins object associated with the master instance managing
            this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`

        """
        super(FreestyleJob, self).__init__(controller, jenkins_master)

    @property
    def scm(self):
        """Gets the object that manages the source code management configuration for a job

        :returns:
            One of several possible plugin objects which exposes the relevant set
            of properties supported by a given source code management tool.
        :rtype: :class:`~.utils.pluginapi.PluginBase`
        """
        xml = self.config_xml
        jobxml = JobXML(xml)
        return jobxml.scm

    @property
    def custom_workspace(self):
        """
        :returns: custom workspace associated with this job
        :rtype: :class:`str`
        """
        xml = self.config_xml

        jobxml = JobXML(xml)
        return jobxml.custom_workspace

    @custom_workspace.setter
    def custom_workspace(self, path):
        """Defines a new custom workspace for the job

        :param str path: new custom workspace path
        """
        xml = self.config_xml

        jobxml = JobXML(xml)
        jobxml.custom_workspace = path

        self.config_xml = jobxml.xml

    @staticmethod
    def template_config_xml():
        """Gets a basic XML configuration template for use when instantiating jobs of this type

        :returns: a basic XML configuration template for use when instantiating jobs of this type
        :rtype: :class:`str`
        """
        xml = """<project>
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
            <builders/>
            <publishers/>
            <buildWrappers/>
            </project>"""
        return xml


if __name__ == "__main__":  # pragma: no cover
    pass
