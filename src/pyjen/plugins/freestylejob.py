"""Primitives that manage Jenkins job of type 'Freestyle'"""
from xml.etree import ElementTree
from pyjen.job import Job
from pyjen.utils.jobxml import JobXML
from pyjen.utils.plugin_api import find_plugin


class FreestyleJob(Job):
    """Jenkins job of type 'freestyle'"""
    # ----------------------------------------------------- XML BASED PROPERTIES
    @property
    def builders(self):
        """list (XMLPlugin): PyJen plugins that manage the various 'builders'
        for this job
        """
        return self._job_xml.builders

    def add_builder(self, builder):
        """Adds a new build step to this job

        Args:
            builder (XMLPlugin):
                PyJen plugin describing the build step to add
        """
        self._job_xml.add_builder(builder)
        self._job_xml.update()

    @property
    def scm(self):
        """XMLPlugin: PyJen plugin describing the source code repository
        configuration for the job"""
        return self._job_xml.scm

    @scm.setter
    def scm(self, value):
        self._job_xml.scm = value.node
        self._job_xml.update()

    @property
    def publishers(self):
        """list (XMLPlugin): all plugins configured as 'publishers' for this job
        """
        return self._job_xml.publishers

    def add_publisher(self, publisher):
        """Adds a new job publisher to this job

        Args:
            publisher (XMLPlugin):
                job publisher to add
        """
        self._job_xml.add_publisher(publisher)
        self._job_xml.update()

    @property
    def custom_workspace(self):
        """str: the custom workspace associated with this job

        May return an empty character string if the custom workspace feature
        is not currently enabled.
        """
        return self._job_xml.custom_workspace or ""

    @custom_workspace.setter
    def custom_workspace(self, path):
        if path == "":
            self._job_xml.disable_custom_workspace()
        else:
            self._job_xml.custom_workspace = path
        self._job_xml.update()

    @property
    def custom_workspace_enabled(self):
        """bool: Checks to see if this job has the custom workspace option
        enabled"""
        return self._job_xml.custom_workspace is not None

    @property
    def quiet_period_enabled(self):
        """bool: Checks to see if a custom quiet period is defined on this job
        """
        return self._job_xml.quiet_period is not None

    @property
    def quiet_period(self):
        """int: the delay, in seconds, builds of this job wait in the queue
        before being run. Returns -1 if there is no custom quiet period for this
        job"""
        # TODO: this property should return 0 when not set, and the value
        # should be returned from the XML class
        return self._job_xml.quiet_period or -1

    @quiet_period.setter
    def quiet_period(self, value):
        if value < 0:
            self._job_xml.disable_quiet_period()
        else:
            self._job_xml.quiet_period = value
        self._job_xml.update()

    @property
    def assigned_node_enabled(self):
        """bool: Checks to see if this job has a custom node restriction"""
        return self._job_xml.assigned_node is not None

    @property
    def assigned_node(self):
        """str: the custom node label restricting which nodes this job can
        run against"""
        return self._job_xml.assigned_node or ""

    @assigned_node.setter
    def assigned_node(self, value):
        if value == "":
            self._job_xml.disable_assigned_node()
        else:
            self._job_xml.assigned_node = value
        self._job_xml.update()

    # ---------------------------------------------------- JSON BASED PROPERTIES
    @property
    def upstream_jobs(self):
        """list (Job):list of upstream dependencies for this job"""
        data = self._api.get_api_data()

        jobs = data['upstreamProjects']

        retval = []

        for j in jobs:
            retval.append(Job.instantiate(j, self._api))

        return retval

    @property
    def all_upstream_jobs(self):
        """list (Job): list of all jobs that this job depends on, recursively

        Includes jobs that trigger this job, and all jobs trigger those
        jobs, recursively for all upstream dependencies
        """

        retval = self.upstream_jobs
        for cur_job in retval:
            retval.extend(cur_job.all_upstream_jobs)
        return retval

    @property
    def downstream_jobs(self):
        """list (Job): list of jobs to be triggered after this job completes"""
        data = self._api.get_api_data()

        jobs = data['downstreamProjects']

        retval = []

        for j in jobs:
            retval.append(Job.instantiate(j, self._api))

        return retval

    @property
    def all_downstream_jobs(self):
        """list (Job): list of all jobs that depend on this job, recursively

        Includes jobs triggered by this job, and all jobs triggered by those
        jobs, recursively for all downstream dependencies
        """
        retval = self.downstream_jobs
        for cur_job in retval:
            retval.extend(cur_job.all_downstream_jobs)

        return retval

    # --------------------------------------------------------------- PLUGIN API
    @property
    def _xml_class(self):
        """FreestyleXML: reference to the Python class that is used to parse
        and manipulate the raw XML associated with this job type"""
        return FreestyleXML

    @staticmethod
    def template_config_xml():
        """
        Returns:
            str: XML configuration template for instantiating jobs of this type
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
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.model.FreeStyleProject"


class FreestyleXML(JobXML):
    """Abstraction around the config.xml for this type of Jenkins job"""

    @property
    def publishers(self):
        """list (XMLPlugin): 0 or more
        post-build publishers associated with this job. Each element will be an
        instance of a compatible PyJen plugin for each publisher. Publishers
        with no valid PyJen plugin installed will be ignored"""
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

    def add_publisher(self, new_publisher):
        """Adds a new publisher node to the publisher section of the job XML

        Args:
            new_publisher (XMLPlugin):
                PyJen plugin which supports the Jenkins publisher API
        """
        pubs = self._root.find('publishers')
        pubs.append(new_publisher.node)
        new_publisher.parent = self

    @property
    def scm(self):
        """Retrieves the appropriate plugin for the SCM portion of a job

        Detects which source code management tool is being used by this
        job, locates the appropriate plugin for that tool, and returns
        an instance of the wrapper for that plugin pre-configured with
        the settings found in the relevant XML subtree.

        Returns:
            XMLPlugin:
                One of any number of plugin objects responsible for providing
                extensions to the source code management portion of a job

                Example: :class:`~.subversion.Subversion`
                Example: :class:`~.gitscm.GitSCM`
        """
        node = self._root.find('scm')
        plugin_class = find_plugin(node.attrib["class"])
        if plugin_class is None:
            raise NotImplementedError(
                "SCM XML plugin not found: " + node.attrib["class"])
        return plugin_class(node)

    @scm.setter
    def scm(self, node):
        cur_scm = self._root.find('scm')
        self._root.remove(cur_scm)
        self._root.append(node)

    @property
    def builders(self):
        """list (XMLPlugin): PyJen plugins that manage the various 'builders'
        for this job
        """
        retval = []
        nodes = self._root.find('builders')
        for node in nodes:
            plugin_class = find_plugin(node.tag)
            if plugin_class is None:
                self._log.warning("Unsupported job 'builder' plugin %s",
                                  node.tag)
                continue
            temp = plugin_class(node)
            temp.parent = self
            retval.append(temp)

        return retval

    def add_builder(self, builder):
        """Adds a new builder node to the build steps section of the job XML

        Args:
            builder (XMLPlugin):
                PyJen plugin implementing the new job builder to be added
        """
        pubs = self._root.find('builders')
        pubs.append(builder.node)
        builder.parent = self

    @property
    def quiet_period(self):
        """int: the delay, in seconds, this job waits in queue before running
        a build

        May return None if no custom quiet period is defined. At the time of
        this writing the default value is 5 seconds however this may change
        over time.
        """
        node = self._root.find("quietPeriod")
        if node is None:
            return None
        return int(node.text)

    @quiet_period.setter
    def quiet_period(self, value):
        node = self._root.find("quietPeriod")
        if node is None:
            node = ElementTree.SubElement(self._root, 'quietPeriod')
        node.text = str(value)

    def disable_quiet_period(self):
        """Disables custom quiet period on a job"""
        node = self._root.find("quietPeriod")
        if node is not None:
            self._root.remove(node)

    @property
    def custom_workspace(self):
        """str: the local path for the custom workspace associated with this
        job. Returns None if the custom workspace option is not enabled"""
        node = self._root.find('customWorkspace')
        if node is None:
            return None
        return node.text

    @custom_workspace.setter
    def custom_workspace(self, path):
        node = self._root.find('customWorkspace')

        if node is None:
            node = ElementTree.SubElement(self._root, 'customWorkspace')

        node.text = path

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace"""
        node = self._root.find('customWorkspace')

        if node is not None:
            self._root.remove(node)

    @property
    def assigned_node(self):
        """str: the build agent label this job is associated with"""
        node = self._root.find("assignedNode")
        if node is None:
            return None
        return node.text

    @assigned_node.setter
    def assigned_node(self, node_label):
        node = self._root.find('assignedNode')

        if node is None:
            node = ElementTree.SubElement(self._root, 'assignedNode')

        node.text = node_label

    def disable_assigned_node(self):
        """Disables a custom node assignment on this job"""
        node = self._root.find('assignedNode')
        if node is not None:
            self._root.remove(node)


PluginClass = FreestyleJob


if __name__ == "__main__":  # pragma: no cover
    pass
