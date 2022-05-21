"""Primitives for interacting with Jenkins jobs"""
import logging
from urllib.parse import urlsplit, urljoin
import requests
from requests.exceptions import HTTPError
from pyjen.build import Build
from pyjen.queue_item import QueueItem
from pyjen.utils.jobxml import JobXML
from pyjen.utils.plugin_api import find_plugin, get_all_plugins


class Job:
    """Abstraction for operations common to all job types on Jenkins"""
    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api
        self._xml_cache = None
        self._log = logging.getLogger(self.__module__)

    def __repr__(self):
        return self._api.url

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return other.name == self.name

    def __ne__(self, other):
        if not isinstance(other, type(self)):
            return True
        return other.name != self.name

    def __hash__(self):
        return hash(self._api.url)

    # ---------------------------------------------- CONFIG XML BASED PROPERTIES
    @property
    def _job_xml(self):
        """JobXML: XML definition for the job configuration"""
        if self._xml_cache is not None:
            return self._xml_cache
        self._xml_cache = self._xml_class(self._api)
        return self._xml_cache

    @property
    def config_xml(self):
        """str: raw XML configuration for the job

        Allows callers to manipulate the raw job configuration definition
        without relying on the PyJen abstractions.

        Warning:
            For advanced use only.
        """
        return self._job_xml.xml

    @config_xml.setter
    def config_xml(self, new_xml):
        self._job_xml.xml = new_xml

    @property
    def properties(self):
        """list (XMLPlugin): custom properties associated with this job,
        typically describing features of the job provided by third party plugins
        """
        return self._job_xml.properties

    def add_property(self, new_property):
        """Adds a new job property to the configuration

        Args:
            new_property (XMLPlugin):
                Custom job property to be added. May be any PyJen plugin that
                supports the Jenkins job property plugin API.
        """
        self._job_xml.add_property(new_property)
        self._job_xml.update()

    @property
    def jenkins_plugin_name(self):
        """str: Extracts the name of the Jenkins plugin providing the features
        associated with this job. May reference any number of third party
        plugins supported by the Jenkins instance being managed.

        The data returned by this helper property is extracted from the
        config XML that defines this job.
        """
        return self._job_xml.plugin_name

    # ---------------------------------------------------- JSON BASED PROPERTIES
    @property
    def name(self):
        """str: the name of the Jenkins job"""
        data = self._api.get_api_data()
        return data['name']

    @property
    def is_disabled(self):
        """bool: True if the job is disabled, otherwise False"""
        data = self._api.get_api_data()

        return data['color'] == "disabled"

    @property
    def is_unstable(self):
        """bool: True if the latest build of the job is unstable, otherwise
        False"""
        data = self._api.get_api_data()

        return data['color'] == "yellow"

    @property
    def is_failing(self):
        """bool: True if the latest build of the job is a failure, otherwise
        False"""
        data = self._api.get_api_data()
        return data['color'] == "red"

    @property
    def has_been_built(self):
        """bool: True if the job has been built at least once, otherwise False
        """
        data = self._api.get_api_data()

        return data['color'] != "notbuilt"

    @property
    def recent_builds(self):
        """list (Build): list of the most recent builds of this job

        Rather than returning all data on all available builds, this
        method only returns the latest 20 or 30 builds. This list is
        synonymous with the short list provided on the main info
        page for the job on the dashboard.
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
        """list (Build): all recorded builds for this job"""
        data = self._api.get_api_data(query_params="tree=allBuilds[url]")

        builds = data['allBuilds']

        retval = []
        for cur_build in builds:
            temp_build = Build(self._api.clone(cur_build['url']))
            retval.append(temp_build)

        return retval

    @property
    def last_good_build(self):
        """Build: the most recent successful build of this job

        Synonymous with the "Last successful build" permalink on the
        jobs' main status page
        """
        data = self._api.get_api_data()

        lgb = data['lastSuccessfulBuild']

        if lgb is None:
            return None

        return Build(self._api.clone(lgb['url']))

    @property
    def last_build(self):
        """Build: the most recent build of this job

        Synonymous with the "Last Build" permalink on the jobs'
        main status page
        """
        data = self._api.get_api_data()

        if 'lastBuild' not in data or data['lastBuild'] is None:
            return None
        last_build = data['lastBuild']

        return Build(self._api.clone(last_build['url']))

    @property
    def last_failed_build(self):
        """Build: the most recent build of this job with a status of "failed"

        Synonymous with the "Last failed build" permalink on the jobs'
        main status page
        """
        data = self._api.get_api_data()

        bld = data['lastFailedBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    @property
    def last_stable_build(self):
        """Build: the most recent build of this job with a status of "stable"

        Synonymous with the "Last stable build" permalink on the jobs'
        main status page
        """
        data = self._api.get_api_data()

        bld = data['lastCompletedBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    @property
    def last_unsuccessful_build(self):
        """Build: the most recent build of this job with a status of "unstable"

        Synonymous with the "Last unsuccessful build" permalink on the jobs'
        main status page
        """
        data = self._api.get_api_data()

        bld = data['lastUnsuccessfulBuild']

        if bld is None:
            return None

        return Build(self._api.clone(bld['url']))

    def find_build_by_queue_id(self, queue_id):
        """the build of this job which correlates to a specific queue item

        Args:
            queue_id (int):

                ID of the build queue item to correlate with. Typically
                extracted from the :meth:`~.queue_item.QueueItem.uid` property.

        Returns:
            Build:
                reference to the build associated with the specified queue id or
                None if no such build exists
        """
        data = {
            "tree": "builds[url,queueId]",
            "xpath": f"//build[queueId={queue_id}]"
        }
        try:
            root_node = self._api.get_api_xml(params=data)
        except HTTPError as err:
            if err.response.status_code == requests.codes.NOT_FOUND:
                return None
            raise

        node = root_node.find("url")
        new_api = self._api.clone(node.text)
        return Build(new_api)

    def disable(self):
        """Disables this job to prevent new builds from being executed

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

    def start_build(self, **kwargs):
        """Forces a build of this job

        Synonymous with a manual trigger. A new instance
        of the job (ie: a build) will be added to the
        appropriate build queue where it will be scheduled
        for execution on the next available agent + executor.

        Args:
            kwargs (dict):
                0 or more named arguments to pass as build parameters to the
                job when triggering the build.

        Returns:
            QueueItem:
                Reference to the Jenkins queue item that tracks the progress
                of the triggered build prior to the build actually running.
        """
        if not kwargs.keys():
            res = self._api.post(self._api.url + "build")
        else:
            params = {"params": kwargs}
            res = self._api.post(self._api.url + "buildWithParameters", params)

        return QueueItem(self._api.clone(res.headers["Location"]))

    def get_build_by_number(self, build_number):
        """Gets a specific build of this job from the build history

        Args:
            build_number (int):
                Numeric identifier of the build to retrieve
                Value is typically non-negative

        Returns:
            Build:
                Reference to the build with the given numeric identifier, or
                None if no such build exists
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
        """Returns a list of all of the builds for a job that occurred between
        the specified start and end times

        Args:
            start_time (datetime.datetime):
                starting time index for range of builds to find
            end_time (datetime.datetime):
                ending time index for range of builds to find

        Returns:
            list (Build):
                list of 0 or more builds of this job that began during the
                time range provided
        """
        if start_time > end_time:
            end_time, start_time = start_time, end_time

        builds = []

        for run in self.all_builds:
            if run.start_time < start_time:
                break
            if end_time >= run.start_time >= start_time:
                builds.append(run)
        return builds

    @property
    def build_health(self):
        """int: the percentage of good builds from recorded history of this job

        This metric is associated with the "weather" icon that can be shown
        next to jobs in certain views
        """
        data = self._api.get_api_data()

        health_report = data['healthReport']

        for cur_report in health_report:
            if "Build stability:" in cur_report["description"]:
                return cur_report["score"]

        return 0

    def clone(self, new_job_name, disable=True):
        """"Create a new job with the same configuration as this one

        Args:
            new_job_name (str):
                Name of the new job to be created
            disable (bool):
                Indicates whether the newly created job should be disabled after
                creation to prevent builds from accidentally triggering
                immediately after creation

        Returns:
            Job:
                reference to the newly created job
        """
        # NOTE: In order to properly support jobs that may contain nested
        #       jobs we have to do some URL manipulations to extrapolate the
        #       REST API endpoint for the parent object to which the cloned
        #       view is to be contained.
        parts = urlsplit(self._api.url).path.split("/")
        parts = [cur_part for cur_part in parts if cur_part.strip()]
        assert len(parts) >= 2
        assert parts[-2] == "job"
        parent_url = urljoin(
            self._api.url, "/" + "/".join(parts[:-2]))

        parent_api = self._api.clone(parent_url)
        args = {
            "params": {
                "name": new_job_name,
                "mode": "copy",
                "from": self.name
            }
        }
        parent_api.post(parent_api.url + "createItem", args=args)

        new_url = parent_api.url + "job/" + new_job_name
        new_api = self._api.clone(new_url)
        new_job = self.__class__(new_api)
        if disable:
            new_job.disable()
        return new_job

    def rename(self, new_job_name):
        """Changes the name of this job

        Args:
            new_job_name (str):
                new name to assign to this job
        """
        args = {
            "params": {
                "newName": new_job_name
            }
        }
        self._api.post(self._api.url + "doRename", args=args)

        # NOTE: In order to properly support jobs that may contain nested
        #       jobs we have to do some URL manipulations to extrapolate the
        #       REST API endpoint for the parent object to which the cloned
        #       view is to be contained.
        parts = urlsplit(self._api.url).path.split("/")
        parts = [cur_part for cur_part in parts if cur_part.strip()]
        assert len(parts) >= 2
        assert parts[-2] == "job"
        new_url = urljoin(
            self._api.url, "/" + "/".join(parts[:-2]))
        new_url += "/job/" + new_job_name
        self._api = self._api.clone(new_url)

        assert self.name == new_job_name

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def instantiate(json_data, rest_api):
        """Factory method for finding the appropriate PyJen view object based
        on data loaded from the Jenkins REST API

        Args:
            json_data (dict):
                data loaded from the Jenkins REST API summarizing the view to be
                instantiated
            rest_api (JenkinsAPI):
                PyJen REST API configured for use by the parent container. Will
                be used to instantiate the PyJen view that is returned.

        Returns:
            Job:
                PyJen job object wrapping the REST API for the given job
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
        """list: list of PyJen plugin classes that derive from this class"""
        retval = []
        for cur_plugin in get_all_plugins():
            if issubclass(cur_plugin, cls):
                retval.append(cur_plugin)
        return retval

    @property
    def _xml_class(self):
        """JobXML: reference to the class used to parse and manipulate the raw
        XML definition for this job type"""
        return JobXML


if __name__ == "__main__":  # pragma: no cover
    pass
