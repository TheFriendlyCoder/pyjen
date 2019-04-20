"""Primitives that manage Jenkins job of type 'Freestyle'"""
from pyjen.job import Job
from pyjen.utils.jobxml import JobXML
from pyjen.utils.plugin_api import find_plugin
from pyjen.exceptions import PluginNotSupportedError


class FreestyleJob(Job):
    """Jenkins job of type 'freestyle'

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(FreestyleJob, self).__init__(api)

    @property
    def builders(self):
        """Gets all plugins configured as 'builders' for this job"""
        jxml = FreestyleXML(self.config_xml)
        return jxml.builders

    def add_builder(self, builder):
        """Adds a new build step to this job

        :param builder: build step config to add"""
        jxml = FreestyleXML(self.config_xml)
        jxml.add_builder(builder.node)
        self.config_xml = jxml.xml

    @property
    def upstream_jobs(self):
        """Gets the list of upstream dependencies for this job

        :returns: A list of 0 or more jobs that this job depends on
        :rtype: :class:`list` of :class:`~.job.Job` objects
        """
        data = self._api.get_api_data()

        jobs = data['upstreamProjects']

        retval = list()

        for j in jobs:
            retval.append(Job.instantiate(j, self._api))

        return retval

    @property
    def all_upstream_jobs(self):
        """list of all jobs that this job depends on, recursively

        Includes jobs that trigger this job, and all jobs trigger those
        jobs, recursively for all upstream dependencies

        :returns: A list of 0 or more jobs this job depend on
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """

        retval = self.upstream_jobs
        for cur_job in retval:
            retval.extend(cur_job.all_upstream_jobs)
        return retval

    @property
    def downstream_jobs(self):
        """Gets the list of jobs to be triggered after this job completes

        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._api.get_api_data()

        jobs = data['downstreamProjects']

        retval = list()

        for j in jobs:
            retval.append(Job.instantiate(j, self._api))

        return retval

    @property
    def all_downstream_jobs(self):
        """list of all jobs that depend on this job, recursively

        Includes jobs triggered by this job, and all jobs triggered by those
        jobs, recursively for all downstream dependencies

        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        retval = self.downstream_jobs
        for cur_job in retval:
            retval.extend(cur_job.all_downstream_jobs)

        return retval

    @property
    def scm(self):
        """Gets the source code repository configuration from the job config"""
        jxml = FreestyleXML(self.config_xml)
        return jxml.scm

    @scm.setter
    def scm(self, value):
        """Changes the SCM configuration for this job"""
        jxml = FreestyleXML(self.config_xml)
        jxml.scm = value.node
        self.config_xml = jxml.xml

    @property
    def publishers(self):
        """Gets all plugins configured as 'publishers' for this job"""
        jxml = FreestyleXML(self.config_xml)
        return jxml.publishers

    def add_publisher(self, publisher):
        """Adds a new job publisher to this job

        :param publisher: job publisher to add"""
        jxml = FreestyleXML(self.config_xml)
        jxml.add_publisher(publisher.node)
        self.config_xml = jxml.xml

    @property
    def custom_workspace(self):
        """
        :returns: custom workspace associated with this job
        :rtype: :class:`str`
        """
        xml = self.config_xml

        jobxml = FreestyleXML(xml)
        return jobxml.custom_workspace

    @custom_workspace.setter
    def custom_workspace(self, path):
        """Defines a new custom workspace for the job

        :param str path: new custom workspace path
        """
        xml = self.config_xml

        jobxml = FreestyleXML(xml)
        jobxml.custom_workspace = path

        self.config_xml = jobxml.xml

    @staticmethod
    def template_config_xml():
        """XML configuration template for  instantiating jobs of this type

        :returns:
            a basic XML configuration template for use when instantiating
            jobs of this type
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

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.model.FreeStyleProject"


class FreestyleXML(JobXML):

    @property
    def publishers(self):
        """list of 0 or more post-build publishers associated with this job

        :returns: a list of post-build publishers associated with this job
        :rtype: :class:`list` of publisher plugins supported by this job
        """
        retval = []
        nodes = self._root.find('publishers')
        for node in nodes:
            plugin_class = find_plugin(node.tag)

            if plugin_class is None:
                self._log.warning("Unsupported job 'publisher' plugin: %s",
                                  node.tag)
                continue

            retval.append(plugin_class(node))

        return retval

    def add_publisher(self, node):
        """Adds a new publisher node to the publisher section of the job XML

        :param node: Elementree XML node for the publisher to assign"""
        pubs = self._root.find('publishers')
        pubs.append(node)

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

            Examples: :class:`~pyjen.plugins.subversion.Subversion`

        :rtype: :class:`~.pluginapi.PluginBase`
        """
        node = self._root.find('scm')
        self._log.debug(node)
        plugin_class = find_plugin(node.attrib["class"])
        if plugin_class is None:
            raise PluginNotSupportedError("SCM XML plugin not found",
                                          node.attrib["class"])
        return plugin_class(node)

    @scm.setter
    def scm(self, node):
        """Defines a new source code manager or a job

        :param node: Elementree XML node for the scm to assign"""
        cur_scm = self._root.find('scm')
        self._root.remove(cur_scm)
        self._root.append(node)

    @property
    def builders(self):
        """Gets a list of 0 or more build operations associated with this job

        :returns: a list of build operations associated with this job
        :rtype: :class:`list` of builder plugins used by this job
        """
        retval = list()
        nodes = self._root.find('builders')
        for node in nodes:
            plugin_class = find_plugin(node.tag)
            if plugin_class is None:
                self._log.warning("Unsupported job 'builder' plugin %s",
                                  node.tag)
                continue

            retval.append(plugin_class(node))

        return retval

    def add_builder(self, node):
        """Adds a new builder node to the build steps section of the job XML

        :param node: Elementree XML node for the builder to assign"""
        pubs = self._root.find('builders')
        pubs.append(node)


PluginClass = FreestyleJob


if __name__ == "__main__":  # pragma: no cover
    pass
