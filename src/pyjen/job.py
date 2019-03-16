"""Primitives for interacting with Jenkins jobs"""
import logging
from pyjen.build import Build
from pyjen.utils.jobxml import JobXML
from pyjen.utils.plugin_api import find_plugin, get_all_plugins


class Job(object):
    """Abstraction for operations common to all job types on Jenkins

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(Job, self).__init__()
        self._api = api

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

    @staticmethod
    def instantiate(json_data, rest_api):
        """Factory method for finding the appropriate PyJen view object based
        on data loaded from the Jenkins REST API

        :param dict json_data:
            data loaded from the Jenkins REST API summarizing the view to be
            instantiated
        :param rest_api:
            PyJen REST API configured for use by the parent container. Will
            be used to instantiate the PyJen view that is returned.
        :returns:
            PyJen view object wrapping the REST API for the given Jenkins view
        :rtype: :class:`~.view.View`
        """
        # TODO: Find some way to cache the json data given inside the view so
        #       we can lazy-load API data. For example, the name of the view
        #       is always included in the json data and therefore queries for
        #       the View name after creation should not require another hit
        #       to the REST API
        log = logging.getLogger(__name__)

        job_url = json_data["url"]

        # Extract the name of the Jenkins plugin associated with this view
        # Sanity Check: make sure the metadata for the view has a "_class"
        #               attribute. I'm pretty sure older version of the Jenkins
        #               core did not expose such an attribute, but all versions
        #               from the past 2+ years or more do appear to include it.
        #               If, for some reason this attribute doesn't exist, we'll
        #               fall back to the default view base class which provides
        #               functionality common to all Jenkins views. For extra
        #               debugging purposes however, we log some debug output
        #               if we ever hit this case so we can investigate the
        #               the details further.
        plugin_class = None
        if "_class" in json_data:
            plugin_class = find_plugin(json_data["_class"])
        else:  # pragma: no cover
            log.debug("Unsupported Jenkins version detected. Jobs are "
                      "expected to have a _class metadata attribute but this "
                      "one does not: %s", json_data)

        if not plugin_class:
            log.debug("Unable to find plugin for class %s", json_data["_class"])
            plugin_class = Job

        return plugin_class(rest_api.clone(job_url))

    @classmethod
    def get_supported_plugins(cls):
        """Returns a list of PyJen plugins that derive from this class

        :rtype: :class:`list` of :class:`class`
        """
        retval = list()
        for cur_plugin in get_all_plugins():
            if issubclass(cur_plugin, cls):
                retval.append(cur_plugin)
        return retval

    @property
    def jenkins_plugin_name(self):
        """Extracts the name of the Jenkins plugin associated with this job

        The data returned by this helper property is extracted from the
        config XML that defines this job.

        :rtype: :class:`str`
        """
        jxml = JobXML(self.config_xml)
        return jxml.plugin_name

    @property
    def name(self):
        """Returns the name of the job managed by this object

        :returns: The name of the job
        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['name']

    @property
    def is_disabled(self):
        """Indicates whether this job is disabled or not

        :returns: True if the job is disabled, otherwise False
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()

        return data['color'] == "disabled"

    @property
    def is_unstable(self):
        """Indicates whether the current state of this job is 'unstable'

        :returns:
            True if the latest build of the job is unsable, otherwise False
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()

        return data['color'] == "yellow"

    @property
    def is_failing(self):
        """Indicates whether the current state of the job is 'failed'

        :returns:
            True if the latest build of the job is a failure, otherwise False
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()
        return data['color'] == "red"

    @property
    def has_been_built(self):
        """Checks to see whether this job has ever been built or not

        :returns: True if the job has been built at least once, otherwise false
        :rtype: :class:`bool`
        """
        data = self._api.get_api_data()

        return data['color'] != "notbuilt"

    @property
    def config_xml(self):
        """Gets the raw XML configuration for the job

        Allows callers to manipulate the raw job configuration file as desired.

        :returns: the full XML tree describing this jobs configuration
        :rtype: :class:`str`
        """
        return self._api.get_text("/config.xml")

    @config_xml.setter
    def config_xml(self, new_xml):
        """Allows a caller to manually override the entire job configuration

        WARNING: This is an advanced method that should only be used in
        rare circumstances. All configuration changes should normally
        be handled using other methods provided on this class.

        :param str new_xml: A complete XML tree compatible with the Jenkins API
        """
        args = {'data': new_xml, 'headers': {'Content-Type': 'text/xml'}}
        self._api.post(self._api.url + "config.xml", args)

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
        data = self._api.get_api_data(query_params="depth=2")

        builds = data['builds']

        retval = []
        for cur_build in builds:
            temp_build = Build(self._api.clone(cur_build['url']))
            retval.append(temp_build)

        return retval

    @property
    def all_builds(self):
        """Gets all recorded builds for this job

        :returns: all recorded builds for this job
        :rtype: :class:`list` of :class:`~.build.Build` objects
        """
        data = self._api.get_api_data(query_params="tree=allBuilds[url]")

        builds = data['allBuilds']

        retval = []
        for cur_build in builds:
            temp_build = Build(self._api.clone(cur_build['url']))
            retval.append(temp_build)

        return retval

    @property
    def last_good_build(self):
        """Gets the most recent successful build of this job

        Synonymous with the "Last successful build" permalink on the
        jobs' main status page

        :returns:
            object that provides information and control for the
            last build which completed with a status of 'success'
            If there are no such builds in the build history,
            this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._api.get_api_data()

        lgb = data['lastSuccessfulBuild']

        if lgb is None:
            return None

        return Build(self._api.clone(lgb['url']))

    @property
    def last_build(self):
        """Returns a reference to the most recent build of this job

        Synonymous with the "Last Build" permalink on the jobs'
        main status page

        :returns:
            object that provides information and control for the
            most recent build of this job.
            If there are no such builds in the build history,
            this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._api.get_api_data()

        last_build = data['lastBuild']

        if last_build is None:
            return None

        return Build(self._api.clone(last_build['url']))

    @property
    def last_failed_build(self):
        """the most recent build of this job with a status of "failed"

        Synonymous with the "Last failed build" permalink on the jobs'
        main status page

        :returns:
            Most recent build with a status of 'failed'. If there are no such
            builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._api.get_api_data()

        bld = data['lastFailedBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    @property
    def last_stable_build(self):
        """the most recent build of this job with a status of "stable"

        Synonymous with the "Last stable build" permalink on the jobs'
        main status page

        :returns:
            Most recent build with a status of 'stable'. If there are no such
            builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._api.get_api_data()

        bld = data['lastCompletedBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    @property
    def last_unsuccessful_build(self):
        """the most recent build of this job with a status of "unstable"

        Synonymous with the "Last unsuccessful build" permalink on the jobs'
        main status page

        :returns:
            Most recent build with a status of 'unstable' If there are no such
            builds in the build history, this method returns None
        :rtype: :class:`~.build.Build`
        """
        data = self._api.get_api_data()

        bld = data['lastUnsuccessfulBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    def disable(self):
        """Disables this job

        Sets the state of this job to disabled so as to prevent the
        job from being triggered.

        Use in conjunction with :py:meth:`.enable` and :py:attr:`.is_disabled`
        to control the state of the job.
        """
        self._api.post(self._api.url + "disable")

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
        self._api.post(self._api.url + "enable")

    def delete(self):
        """Deletes this job from the Jenkins dashboard"""
        self._api.post(self._api.url + "doDelete")

    def start_build(self):
        """Forces a build of this job

        Synonymous with a manual trigger. A new instance
        of the job (ie: a build) will be added to the
        appropriate build queue where it will be scheduled
        for execution on the next available agent + executor.
        """
        self._api.post(self._api.url + "build")

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
        # Generate URL where the specified build "should" be
        # TODO: Find some way to efficiently search through all builds to
        #       locate the one with the correct number this would still
        #       require 1 hit to the REST API but would be more robust than
        #       trying to "guess" the correct URL endpoint
        temp_url = self._api.url + str(build_number)
        retval = Build(self._api.clone(temp_url))

        # query the REST API to make sure the URL is correct and that it
        # returns the correct build number
        try:
            assert retval.number == build_number
        except:  # pylint: disable=broad-except,bare-except
            return None

        return retval

    def get_builds_in_time_range(self, start_time, end_time):
        """ Returns a list of all of the builds for a job that
            occurred between the specified start and end times

            :param datetime start_time:
                starting time index for range of builds to find
            :param datetime end_time:
                ending time index for range of builds to find
            :returns: a list of 0 or more builds
            :rtype: :class:`list` of :class:`~.build.Build` objects
        """
        if start_time > end_time:
            end_time, start_time = start_time, end_time

        builds = []

        for run in self.all_builds:
            if run.start_time < start_time:
                break
            elif end_time >= run.start_time >= start_time:
                builds.append(run)
        return builds

    @property
    def quiet_period(self):
        """
        :returns:
            the delay, in seconds, builds of this job wait in the queue before
            being run
        :rtype: :class:`int`
        """
        jobxml = JobXML(self.config_xml)
        return jobxml.quiet_period

    @quiet_period.setter
    def quiet_period(self, value):
        jobxml = JobXML(self.config_xml)
        jobxml.quiet_period = value
        self.config_xml = jobxml.xml

    @property
    def properties(self):
        """all plugins configured as extra configuration properties"""
        jxml = JobXML(self.config_xml)
        return jxml.properties

    @property
    def build_health(self):
        """Gets the percentage of good builds from recorded history of this job

        This metric is associated with the "weather" icon that can be shown
        next to jobs in certain views

        :return: percentage of good builds on record for this job
        :rtype: :class:`int`
        """
        data = self._api.get_api_data()

        health_report = data['healthReport']

        for cur_report in health_report:
            if "Build stability:" in cur_report["description"]:
                return cur_report["score"]

        return 0


if __name__ == "__main__":  # pragma: no cover
    pass
