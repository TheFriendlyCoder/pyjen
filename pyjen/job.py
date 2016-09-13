"""Primitives for interacting with Jenkins jobs"""
from pyjen.build import Build
from pyjen.utils.pluginapi import PluginBase, get_job_plugins, get_plugin_name, find_plugin, init_extension_plugin
from pyjen.exceptions import PluginNotSupportedError
from pyjen.utils.jobxml import JobXML
import xml.etree.ElementTree as ElementTree


class Job(PluginBase):
    """ 'Abstract' base class used by all job classes, providing functionality common to them all"""

    def __init__(self, controller, jenkins_master):
        """
        :param controller: IO interface which manages interaction with the live Jenkins job
        :type controller: :class:`~.datarequester.DataRequester`
        :param jenkins_master: Jenkins instance containing this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        """
        self._controller = controller
        self._master = jenkins_master
        self._name = None
        self._type = None

    def __eq__(self, other):
        """equality operator"""
        if not isinstance(other, Job):
            return False
        return other.name == self.name

    def __ne__(self, other):
        """inequality operator"""
        if not isinstance(other, Job):
            return True
        return other.name != self.name

    def __hash__(self):
        """Hashing function, allowing object to be serialized and compared"""
        return hash(self.name)

    @property
    def type(self):
        if self._type is None:
            node = ElementTree.fromstring(self._controller.config_xml)
            self._type = get_plugin_name(node)
        return self._type

    @staticmethod
    def create(controller, jenkins_master):
        """Factory method used to instantiate the appropriate job type for a given configuration

        :param controller: IO interface to the Jenkins API. This object is expected to be pre-initialized
            with the connection parameters for the job to be processed.
        :type controller: :class:`~.datarequester.DataRequester`
        :param jenkins_master: Jenkins instance containing this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        :return: An instance of the appropriate derived type for the given job
        :rtype: :class:`~.job.Job`
        """
        return Job(controller, jenkins_master).derived_object

    @property
    def derived_object(self):
        """Looks for a custom plugin supporting the specific type of job managed by this object"""
        # check to see if we're trying to derive an object from an already derived object
        if type(self) is not Job:
            return self

        plugin = init_extension_plugin(self._controller, self._master)
        if plugin is not None:
            return plugin

        raise PluginNotSupportedError("Job plugin {0} not found".format(self.type), self.type)

    @staticmethod
    def _create(controller, jenkins_master, job_name):
        """Private helper method for use by other classes in the PyJen API, allowing the instantiation of this
        abstract base class for internal optimizations

        :param controller: IO interface to the Jenkins API. This object is expected to be pre-initialized
            with the connection parameters for the job to be processed.
        :type controller: :class:`~.datarequester.DataRequester`
        :param jenkins_master: Jenkins instance containing this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        :param str job_name: The unique descriptive name for the newly created job
        :return: An instance of the appropriate derived type for the given job
        :rtype: :class:`~.job.Job`
        """
        class PartialJob(Job):
            def __init__(self, local_controller, local_master):
                super(PartialJob, self).__init__(local_controller, local_master)
            type = "Undefined"

        retval = PartialJob(controller, jenkins_master)
        retval._name = job_name
        return retval

    @staticmethod
    def template_config_xml(job_type):
        """Generates a generic configuration file for use when creating a new job on the live Jenkins instance

        :param str job_type: the type descriptor of the job being created
            For valid values see the :py:meth:`.supported_types` method
        :return: XML configuration data for the specified job type
        :rtype: :class:`str`
        """
        plugin = find_plugin(job_type)
        if plugin is not None:
            return plugin.template_config_xml()

        raise PluginNotSupportedError("Job plugin {0} not found".format(job_type), job_type)

    @staticmethod
    def supported_types():
        """Returns a list of all job types supported by this instance of PyJen

        These job types can be used in such methods as :py:meth:`~.jenkins.Jenkins.create_job`, which take as input
        a job type classifier

        :return: list of all job types supported by this instance of PyJen, including those supported by plugins
        :rtype: :class:`str`
        """
        retval = []
        for plugin in get_job_plugins():
            retval.append(plugin.type)

        return retval

    @property
    def name(self):
        """Returns the name of the job managed by this object

        :returns: The name of the job
        :rtype: :class:`str`
        """
        if self._name is not None:
            return self._name

        data = self._controller.get_api_data()
        return data['name']
        
    @property
    def url(self):
        """Returns the URL to the job

        :returns: The URL of the job
        :rtype: :class:'str'
        """
        return self._controller.url

    @property
    def is_disabled(self):
        """Indicates whether this job is disabled or not

        :returns: True if the job is disabled, otherwise False
        :rtype: :class:`bool`
        """
        data = self._controller.get_api_data()

        return data['color'] == "disabled"

    @property
    def has_been_built(self):
        """Checks to see whether this job has ever been built or not

        :returns: True if the job has been built at least once, otherwise false
        :rtype: :class:`bool`
        """

        data = self._controller.get_api_data()

        return data['color'] != "notbuilt"

    @property
    def config_xml(self):
        """Gets the raw XML configuration for the job

        Allows callers to manipulate the raw job configuration file as desired.

        :returns: the full XML tree describing this jobs configuration
        :rtype: :class:`str`
        """
        return self._controller.config_xml

    @config_xml.setter
    def config_xml(self, new_xml):
        """Allows a caller to manually override the entire job configuration

        WARNING: This is an advanced method that should only be used in
        rare circumstances. All configuration changes should normally
        be handled using other methods provided on this class.

        :param str new_xml: A complete XML tree compatible with the Jenkins API
        """
        self._controller.config_xml = new_xml

    @property
    def upstream_jobs(self):
        """Gets the list of upstream dependencies for this job

        :returns: A list of 0 or more jobs that this job depends on
        :rtype: :class:`list` of :class:`~.job.Job` objects
        """
        data = self._controller.get_api_data()

        jobs = data['upstreamProjects']

        retval = []

        for j in jobs:
            temp_data_io = self._controller.clone(j['url'])
            temp_job = Job.create(temp_data_io, self._master)
            retval.append(temp_job)

        return retval

    @property
    def all_upstream_jobs(self):
        """Gets the list of all jobs that this job depends on, including all indirect descendants

        Includes jobs that trigger this job, and all jobs trigger those
        jobs, recursively for all upstream dependencies

        :returns: A list of 0 or more jobs this job depend on
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._controller.get_api_data()
        jobs = data['upstreamProjects']
        retval = []

        for j in jobs:
            temp_data_io = self._controller.clone(j['url'])
            temp_job = Job.create(temp_data_io, self._master)
            retval.append(temp_job)
            retval.extend(temp_job.all_upstream_jobs)

        return retval

    @property
    def recent_builds(self):
        """Gets a list of the most recent builds for this job

        Rather than returning all data on all available builds, this
        method only returns the latest 20 or 30 builds. This list is
        synonymous with the short list provided on the main info
        page for the job on the dashboard.

        :returns: a list of the most recent builds for this job
        :rtype: :class:`list` of :class:`~.build.Build` objects
        """
        data = self._controller.get_api_data(query_params="depth=2")

        builds = data['builds']

        retval = []
        for cur_build in builds:
            temp_data_io = self._controller.clone(cur_build['url'])
            temp_data_io.set_api_data(cur_build)
            temp_build = Build(temp_data_io)
            retval.append(temp_build)

        return retval

    @property
    def all_builds(self):
        """Gets all recorded builds for this job

        :returns: all recorded builds for this job
        :rtype: :class:`list` of :class:`~.build.Build` objects
        """
        data = self._controller.get_api_data(query_params="tree=allBuilds[url]")

        builds = data['allBuilds']

        retval = []
        for cur_build in builds:
            temp_data_io = self._controller.clone(cur_build['url'])
            temp_build = Build(temp_data_io)
            retval.append(temp_build)

        return retval

    @property
    def last_good_build(self):
        """Gets the most recent successful build of this job

        Synonymous with the "Last successful build" permalink on the jobs' main status page


        :returns:
            object that provides information and control for the
            last build which completed with a status of 'success'
            If there are no such builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._controller.get_api_data()

        lgb = data['lastSuccessfulBuild']

        if lgb is None:
            return None

        temp_data_io = self._controller.clone(lgb['url'])
        return Build(temp_data_io)

    @property
    def last_build(self):
        """Returns a reference to the most recent build of this job

        Synonymous with the "Last Build" permalink on the jobs' main status page

        :returns:
            object that provides information and control for the
            most recent build of this job.
            If there are no such builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._controller.get_api_data()

        last_build = data['lastBuild']

        if last_build is None:
            return None

        temp_data_io = self._controller.clone(last_build['url'])
        return Build(temp_data_io)

    @property
    def last_failed_build(self):
        """Returns a reference to the most recent build of this job with a status of "failed"

        Synonymous with the "Last failed build" permalink on the jobs' main status page

        :returns:
            Most recent build with a status of 'failed'
            If there are no such builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._controller.get_api_data()

        bld = data['lastFailedBuild']

        if bld is None:
            return None

        temp_data_io = self._controller.clone(bld['url'])
        return Build(temp_data_io)

    @property
    def last_stable_build(self):
        """Returns a reference to the most recent build of this job with a status of "stable"

        Synonymous with the "Last stable build" permalink on the jobs' main status page


        :returns:
            Most recent build with a status of 'stable'
            If there are no such builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._controller.get_api_data()

        bld = data['lastCompletedBuild']

        if bld is None:
            return None

        temp_data_io = self._controller.clone(bld['url'])
        return Build(temp_data_io)

    @property
    def last_unsuccessful_build(self):
        """Returns a reference to the most recent build of this job with a status of "unstable"

        Synonymous with the "Last unsuccessful build" permalink on the jobs' main status page

        :returns:
            Most recent build with a status of 'unstable'
            If there are no such builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._controller.get_api_data()

        bld = data['lastUnsuccessfulBuild']

        if bld is None:
            return None

        temp_data_io = self._controller.clone(bld['url'])
        return Build(temp_data_io)

    @property
    def downstream_jobs(self):
        """Gets the list of jobs to be triggered after this job completes

        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._controller.get_api_data()

        jobs = data['downstreamProjects']

        retval = []

        for j in jobs:
            temp_data_io = self._controller.clone(j['url'])
            temp_job = Job.create(temp_data_io, self._master)
            retval.append(temp_job)

        return retval

    @property
    def all_downstream_jobs(self):
        """Gets the list of all jobs that depend on this job, including all indirect descendants

        Includes jobs triggered by this job, and all jobs triggered by those
        jobs, recursively for all downstream dependencies

        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._controller.get_api_data()

        jobs = data['downstreamProjects']

        retval = []

        for j in jobs:
            temp_data_io = self._controller.clone(j['url'])
            temp_job = Job.create(temp_data_io, self._master)
            retval.append(temp_job)
            retval.extend(temp_job.all_downstream_jobs)

        return retval

    def disable(self):
        """Disables this job

        Sets the state of this job to disabled so as to prevent the
        job from being triggered.

        Use in conjunction with :py:meth:`.enable` and :py:attr:`.is_disabled`
        to control the state of the job.
        """
        self._controller.post("/disable")

    def enable(self):
        """Enables this job

        If this jobs current state is disabled, it will be
        re-enabled after calling this method. If the job
        is already enabled then this method does nothing.

        Enabling a job allows it to be triggered, either automatically
        via commit hooks / polls or manually through the dashboard.

        Use in conjunction with :py:meth:`.disable` and :py:attr:`.is_disabled`
        to control the state of the job
        """
        self._controller.post("/enable")

    def delete(self):
        """Deletes this job from the Jenkins dashboard"""
        self._controller.post("/doDelete")

    def start_build(self):
        """Forces a build of this job

        Synonymous with a manual trigger. A new instance
        of the job (ie: a build) will be added to the
        appropriate build queue where it will be scheduled
        for execution on the next available agent + executor.
        """
        self._controller.post("/build")

    def get_build_by_number(self, build_number):
        """Gets a specific build of this job from the build history

        :param int build_number:
            Numeric identifier of the build to retrieve
            Value is typically non-negative
        :returns:
            Build object for the build with the given numeric identifier
            If such a build does not exist, returns None
        :rtype: :class:`~.build.Build`
        """
        temp_data_io = self._controller.clone(self._controller.url + str(build_number))

        # Lets try loading data from the given URL to see if it is valid.
        # If it's not valid we'll assume a build with the given number doesn't exist
        try:
            temp_data_io.get_api_data()
        except AssertionError:
            return None

        return Build(temp_data_io)

    def get_builds_in_time_range(self, start_time, end_time):
        """ Returns a list of all of the builds for a job that
            occurred between the specified start and end times

            :param datetime start_time: starting time index for range of builds to find
            :param datetime end_time: ending time index for range of builds to find
            :returns: a list of 0 or more builds
            :rtype: :class:`list` of :class:`~.build.Build` objects
        """
        if start_time > end_time:
            tmp = end_time
            end_time = start_time
            start_time = tmp

        builds = []

        for run in self.all_builds:
            if run.start_time < start_time:
                break
            elif end_time >= run.start_time >= start_time:
                builds.append(run)
        return builds

    def clone(self, new_job_name):
        """"Create a new job with the same configuration as this one

        :param str new_job_name: Name of the new job to be created
        """
        self._master._clone_job(self.name, new_job_name)

    @property
    def publishers(self):
        """Gets all plugins configured as 'publishers' for this job"""
        jxml = JobXML(self.config_xml)
        return jxml.publishers

    @property
    def properties(self):
        """Gets all plugins configured as extra configuration properties for this job"""
        jxml = JobXML(self.config_xml)
        return jxml.properties

    @property
    def builders(self):
        """Gets all plugins configured as 'builders' for this job"""
        jxml = JobXML(self.config_xml)
        return jxml.builders

    @property
    def build_health(self):
        """Gets the percentage of good builds from recorded history of this job

        This metric is associated with the "weather" icon that can be shown next to jobs in certain views
        :return: percentage of good builds on record for this job
        :rtype: :class:`int`
        """
        data = self._controller.get_api_data()

        health_report = data['healthReport']

        for cur_report in health_report:
            if cur_report["description"].find("Build stability:") >= 0:
                return cur_report["score"]

        return 0


if __name__ == "__main__":  # pragma: no cover
    for i in Job.supported_types():
        print(i)
    pass
