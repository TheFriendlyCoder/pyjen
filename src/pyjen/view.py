"""Primitives for interacting with Jenkins views"""
import logging
from pyjen.job import Job
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.plugin_api import find_plugin


class View(object):
    """generic Jenkins views providing interfaces common to all view types

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :param parent:
        PyJen object that "owns" this view. Typically this is a reference to
        the :class:`pyjen.jenkins.Jenkins` object for the current Jenkins
        instance but in certain cases this may be a different object like
        a :class:`pyjen.plugins.nestedview.NestedView`.

        The parent object is expected to expose a method named `create_view`
        which can be used to clone instances of this view.
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """
    def __init__(self, api, parent):
        super(View, self).__init__()
        self._log = logging.getLogger(__name__)
        self._api = api
        self._parent = parent

    @staticmethod
    def instantiate(json_data, rest_api, parent):
        """Factory method for finding the appropriate PyJen view object based
        on data loaded from the Jenkins REST API

        :param dict json_data:
            data loaded from the Jenkins REST API summarizing the view to be
            instantiated
        :param rest_api:
            PyJen REST API configured for use by the parent container. Will
            be used to instantiate the PyJen view that is returned.
        :param parent:
            PyJen object that "owns" the new View object being instantiated
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

        return plugin_class(rest_api.clone(view_url), parent)

    @property
    def name(self):
        """Gets the display name for this view

        This is the name as it appears in the tabbed view
        of the main Jenkins dashboard

        :returns: the name of the view
        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['name']

    @property
    def jobs(self):
        """Gets a list of jobs associated with this view

        Views are simply filters to help organize jobs on the
        Jenkins dashboard. This method returns the set of jobs
        that meet the requirements of the filter associated
        with this view.

        :returns: list of 0 or more jobs that are included in this view
        :rtype:  :class:`list` of :class:`~.job.Job` objects
        """
        data = self._api.get_api_data(query_params="depth=2")

        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:
            retval.append(Job(self._api.clone(j['url'])))

        return retval

    @property
    def config_xml(self):
        """Gets the raw configuration data in XML format

        This is an advanced function which allows the caller
        to manually manipulate the raw configuration settings
        of the view. Use with caution.

        This method allows callers to dynamically update arbitrary properties
        of this view.

        :returns:
            returns the raw XML of the views configuration in
            a plain text string format
        :rtype: :class:`str`
        """
        return self._api.get_text("/config.xml")

    @config_xml.setter
    def config_xml(self, new_xml):
        """Updates the raw config of this view with a new set of properties

        :param str new_xml:
            XML encoded text string to be used as a replacement for the
            current configuration being used by this view.

            NOTE: It is assumed that this input text meets the schema
            requirements for a Jenkins view.
        """
        args = {'data': new_xml, 'headers': {'Content-Type': 'text/xml'}}
        self._api.post(self._api.url + "config.xml", args)

    def delete(self):
        """Deletes this view from the dashboard"""
        self._api.post(self._api.url + "doDelete")

    def delete_all_jobs(self):
        """allows callers to do bulk deletes of all jobs found in this view"""
        for j in self.jobs:
            j.delete()

    def disable_all_jobs(self):
        """allows caller to bulk-disable all jobs found in this view"""
        for j in self.jobs:
            j.disable()

    def enable_all_jobs(self):
        """allows caller to bulk-enable all jobs found in this view"""
        for j in self.jobs:
            j.enable()

    def clone(self, new_view_name):
        """Make a copy of this view with the specified name

        :param str new_view_name: name of the newly cloned view
        :return: reference to the View object that manages the new, cloned view
        :rtype: :class:`~.view.View`
        """
        vxml = ViewXML(self.config_xml)
        new_view = self._parent.create_view(new_view_name, vxml.plugin_name)

        vxml.rename(new_view_name)
        new_view.config_xml = vxml.xml
        return new_view

    def rename(self, new_name):
        """Rename this view

        Since Jenkins doesn't currently support renaming views, this method
        destroys the current view and creates a new one with the same
        configuration. As such, once this method completes this object will
        become invalidated

        :param str new_name: new name for this view
        :returns: reference to the newly create view
        """
        new_view = self.clone(new_name)
        self.delete()
        return new_view

    @property
    def view_metrics(self):
        """Composes a report on the jobs contained within the view

        :return: Dictionary containing metrics about the view
        :rtype: :class:`dict`
        """
        data = self._api.get_api_data()

        broken_jobs = []
        disabled_jobs = []
        unstable_jobs = []
        broken_job_count = 0
        disabled_jobs_count = 0
        unstable_job_count = 0

        for job in data["jobs"]:

            # TODO: Figure out how to prepopulate name field here
            #temp_job = Job._create(temp_data_io, self._master, job['name'])
            temp_job = Job(self._api.clone(job['url']))

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

    # TODO: Add a supported_types static method for returning all plugins
    #  which extend the View data type


if __name__ == "__main__":  # pragma: no cover
    pass
