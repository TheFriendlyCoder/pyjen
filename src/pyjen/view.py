"""Primitives for interacting with Jenkins views"""
import logging
from urllib.parse import urljoin, urlsplit
from pyjen.job import Job
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.plugin_api import find_plugin, get_all_plugins
from pyjen.utils.helpers import create_view


class View:
    """generic Jenkins views providing interfaces common to all view types"""
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

    @property
    def name(self):
        """str: the name as it appears in the tabbed view of the main Jenkins
        dashboard"""
        data = self._api.get_api_data()
        return data['name']

    @property
    def jobs(self):
        """list (Job): list of 0 or more jobs associated with this view

        Views are simply filters to help organize jobs on the
        Jenkins dashboard. This method returns the set of jobs
        that meet the requirements of the filter associated
        with this view.
        """
        data = self._api.get_api_data(query_params="depth=0")

        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:
            retval.append(Job.instantiate(j, self._api))

        return retval

    def delete(self):
        """Deletes this view from the dashboard"""
        self._api.post(self._api.url + "doDelete")

    def delete_all_jobs(self):
        """Batch operation that deletes all jobs found in this view"""
        for j in self.jobs:
            j.delete()

    def disable_all_jobs(self):
        """Batch operation that disables all jobs found in this view"""
        for j in self.jobs:
            j.disable()

    def enable_all_jobs(self):
        """Batch operation that enables all jobs found in this view"""
        for j in self.jobs:
            j.enable()

    @property
    def view_metrics(self):
        """dict: Composes a report on the jobs contained within the view"""
        data = self._api.get_api_data()

        broken_jobs = []
        disabled_jobs = []
        unstable_jobs = []
        broken_job_count = 0
        disabled_jobs_count = 0
        unstable_job_count = 0

        for job in data["jobs"]:

            temp_job = Job.instantiate(job, self._api)

            if temp_job.is_failing:
                broken_job_count += 1
                broken_jobs.append(temp_job)
            elif temp_job.is_disabled:
                disabled_jobs_count += 1
                disabled_jobs.append(temp_job)
            elif temp_job.is_unstable:
                unstable_job_count += 1
                unstable_jobs.append(temp_job)

        return {"broken_jobs_count": broken_job_count,
                "disabled_jobs_count": disabled_jobs_count,
                "unstable_jobs_count": unstable_job_count,
                "broken_jobs": broken_jobs,
                "unstable_jobs": unstable_jobs,
                "disabled_jobs": disabled_jobs}

    def _clone_view_helper(self, new_view_name):
        """Internal helper method used by the :py:meth:`.clone` method.
        Generates the XML definition for the view being created as part
        of the clone operation

        Args:
            new_view_name (str):
                name of the new view being created

        Returns:
            tuple:
                Reference to the :class:`~.utils.jenkins_api.JenkinsAPI` and
                :class:`~.utils.viewxml.ViewXML` defining the configuration for
                the new view to be created from this one.
        """
        # NOTE: In order to properly support views that may contain nested
        #       views we have to do some URL manipulations to extrapolate the
        #       REST API endpoint for the parent object to which the cloned
        #       view is to be contained.
        parts = urlsplit(self._api.url).path.split("/")
        parts = [cur_part for cur_part in parts if cur_part.strip()]
        assert len(parts) >= 2
        assert parts[-2] == "view"
        parent_url = urljoin(
            self._api.url, "/" + "/".join(parts[:-2]))

        # Ask the parent object to create a new view of the same type
        # as the current view
        parent_api = self._api.clone(parent_url)
        create_view(parent_api, new_view_name, self.__class__)

        # Save a backup copy of the original config XML with the view
        # name changed
        temp_view_xml = self._view_xml
        temp_view_xml.rename(new_view_name)
        updated_xml = temp_view_xml.xml

        # Update our REST API object to point to the endpoint associated
        # with the newly created view
        new_url = urljoin(
            parent_api.url, "view/" + new_view_name)
        updated_api = self._api.clone(new_url)

        return updated_api, updated_xml

    def clone(self, new_view_name):
        """Make a copy of this view with the specified name

        Args:
            new_view_name (str):
                name to give the newly created view

        Returns:
            View:
                reference to the created view, with the same configuration
                options as this one
        """
        updated_api, updated_xml = self._clone_view_helper(new_view_name)
        retval = self.__class__(updated_api)
        retval.config_xml = updated_xml
        return retval

    def rename(self, new_view_name):
        """Changes the name of this view

        Args:
            new_view_name (str):
                new name for this view
        """
        updated_api, updated_xml = self._clone_view_helper(new_view_name)

        # Invalidate the current view
        self.delete()

        # Update our REST API object to point to the endpoint associated
        # with the newly created view
        self._api = updated_api

        # Finally, make sure the full XML configuration from the original
        # view is copied to the newly created view
        self._xml_cache = None
        self._view_xml.xml = updated_xml

    # ---------------------------------------------- CONFIG XML BASED PROPERTIES
    @property
    def _view_xml(self):
        """ViewXML: reference to the object that can parse and manipulate the
        raw XML definition for this view"""
        if self._xml_cache is not None:
            return self._xml_cache
        self._xml_cache = self._xml_class(self._api)
        return self._xml_cache

    @property
    def jenkins_plugin_name(self):
        """str: Extracts the name of the Jenkins plugin associated with this
        View

        The data returned by this helper property is extracted from the
        config XML that defines this job.
        """
        return self._view_xml.plugin_name

    @property
    def config_xml(self):
        """str: the raw XML configuration for the view

        Allows callers to manipulate the raw view configuration file as desired.

        Warning:
            For advanced use only.
        """
        return self._view_xml.xml

    @config_xml.setter
    def config_xml(self, new_xml):
        self._view_xml.xml = new_xml

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
            View:
                PyJen view object wrapping the REST API for the given view
        """
        # TODO: Find some way to cache the json data given inside the view so
        #       we can lazy-load API data. For example, the name of the view
        #       is always included in the json data and therefore queries for
        #       the View name after creation should not require another hit
        #       to the REST API
        log = logging.getLogger(__name__)
        # The default view will not have a valid view URL
        # so we need to look for this and generate a corrected one
        view_url = json_data["url"]
        if '/view/' not in view_url:
            view_url = view_url + "view/" + json_data["name"]

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
            log.debug("Unsupported Jenkins version detected. Views are "
                      "expected to have a _class metadata attribute but this "
                      "one does not: %s", json_data)

        if not plugin_class:
            log.debug("Unable to find plugin for class %s", json_data["_class"])
            plugin_class = View

        return plugin_class(rest_api.clone(view_url))

    @classmethod
    def get_supported_plugins(cls):
        """list: list of PyJen plugin classes that may be used to instantiate
        views on this Jenkins instance"""
        retval = []
        for cur_plugin in get_all_plugins():
            if issubclass(cur_plugin, cls):
                retval.append(cur_plugin)
        return retval

    @property
    def _xml_class(self):
        """ViewXML: class that is able to parse and manipulate the raw XML
        that defines the configuration for this view"""
        return ViewXML


if __name__ == "__main__":  # pragma: no cover
    pass
