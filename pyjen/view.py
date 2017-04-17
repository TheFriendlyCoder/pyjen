"""Primitives for interacting with Jenkins views"""
from pyjen.job import Job
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.jenkins_api import JenkinsAPI


class View(JenkinsAPI):
    """ Abstraction for generic Jenkins views providing interfaces common to all view types

    :param str url: Full URL of a view on a Jenkins master
    """
    def __init__(self, url):
        super(View, self).__init__(url)
        self._type = None

    @property
    def derived_object(self):
        """Looks for a custom plugin supporting the specific type of view managed by this object"""
        # check to see if we're trying to derive an object from an already derived object
        if not isinstance(self, View):
            return self

        xml_obj = ViewXML(self.config_xml)

        return xml_obj.derived_object()

    @property
    def name(self):
        """Gets the display name for this view

        This is the name as it appears in the tabbed view
        of the main Jenkins dashboard

        :returns: the name of the view
        :rtype: :class:`str`
        """
        data = self.get_api_data()
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
        data = self.get_api_data(query_params="depth=2")

        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:
            # TODO: Find a way to prepoulate api data
            # temp_data_io.set_api_data(j)
            retval.append(Job(j['url']))

        return retval

    @property
    def config_xml(self):
        """Gets the raw configuration data in XML format

        This is an advanced function which allows the caller
        to manually manipulate the raw configuration settings
        of the view. Use with caution.

        This method allows callers to dynamically update arbitrary properties of this view.

        :returns:
            returns the raw XML of the views configuration in
            a plain text string format
        :rtype: :class:`str`
        """
        return self.get_text("/config.xml")

    @config_xml.setter
    def config_xml(self, new_xml):
        """Updates the raw configuration of this view with a new set of properties

        :param str new_xml:
            XML encoded text string to be used as a replacement for the
            current configuration being used by this view.

            NOTE: It is assumed that this input text meets the schema
            requirements for a Jenkins view.
        """
        args = {'data': new_xml, 'headers': {'Content-Type': 'text/xml'}}
        self.post(self.url + "config.xml", args)

    def delete(self):
        """Deletes this view from the dashboard"""
        self.post(self.url + "doDelete")

    def delete_all_jobs(self):
        """Batch method that allows callers to do bulk deletes of all jobs found in this view"""
        for j in self.jobs:
            j.delete()

    def disable_all_jobs(self):
        """Batch method that allows caller to bulk-disable all jobs found in this view"""
        for j in self.jobs:
            j.disable()

    def enable_all_jobs(self):
        """Batch method that allows caller to bulk-enable all jobs found in this view"""
        for j in self.jobs:
            j.enable()

    def clone_all_jobs(self, source_job_name_pattern, new_job_substring):
        """Batch-clones all jobs contained within this view

        :param str source_job_name_pattern:
            pattern to use as a substitution rule when generating new names for cloned jobs. Substrings within the
            existing job names that match this pattern will be replaced by the given substitution string
        :param str new_job_substring:
            character string used to generate new job names for the clones of the existing jobs. The substring
            of an existing job that matches the given regex will be replaced by this new string to create the
            new job name for it's cloned counterpart.
        """
        retval = []
        for cur_job in self.jobs:
            new_name = cur_job.name.replace(source_job_name_pattern, new_job_substring)
            new_job = cur_job.clone(new_name)
            retval.append(new_job)
        return retval

    def clone(self, new_view_name):
        """Make a copy of this view with the specified name

        :param str new_view_name: name of the newly cloned view
        :return: reference to the View object that manages the new, cloned view
        :rtype: :class:`~.view.View`
        """
        vxml = ViewXML(self.config_xml)
        self._create_view(new_view_name, vxml.plugin_name() or vxml.plugin_class_name())

        new_url = self.url.replace(self.name, new_view_name)
        new_view = View(new_url)

        vxml.rename(new_view_name)
        new_view.config_xml = vxml.xml
        return new_view

    def rename(self, new_name):
        """Rename this view

        Since Jenkins doesn't currently support renaming views, this method destroys the current view and creates
        a new one with the same configuration. As such, once this method completes this object will become invalidated

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
        data = self.get_api_data()

        broken_jobs = []
        disabled_jobs = []
        unstable_jobs = []
        broken_job_count = 0
        disabled_jobs_count = 0
        unstable_job_count = 0

        for job in data["jobs"]:

            # TODO: Figure out how to prepopulate name field here
            #temp_job = Job._create(temp_data_io, self._master, job['name'])
            temp_job = Job(job['url'])

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

    # TODO: Add a supported_types static method for returning all plugins which extend the View data type

if __name__ == "__main__":  # pragma: no cover
    #for i in View.supported_types():
    #    print(i)
    pass
