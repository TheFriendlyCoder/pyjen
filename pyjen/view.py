"""Primitives for interacting with Jenkins views"""
from pyjen.job import Job
from pyjen.exceptions import PluginNotSupportedError
from pyjen.utils.pluginapi import get_plugins, PluginBase, PluginXML
from pyjen.utils.viewxml import ViewXML
import logging

log = logging.getLogger(__name__)


class View(PluginBase):
    """ 'Abstract' base class used by all view classes, providing functionality common to them all"""

    def __init__(self, data_io_controller, jenkins_master):
        """
        :param data_io_controller: IO interface which manages interaction with the live Jenkins view
        :type data_io_controller: :class:`~.datarequester.DataRequester`
        :param jenkins_master: Jenkins instance containing this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        """
        self._controller = data_io_controller
        self._master = jenkins_master

    @staticmethod
    def create(controller, jenkins_master):
        """Factory method used to instantiate the appropriate view type for a given configuration

        :param controller: IO interface to the Jenkins API. This object is expected to be pre-initialized
            with the connection parameters for the view to be processed.
        :type controller: :class:`~.datarequester.DataRequester`
        :param jenkins_master: Jenkins instance containing this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        :return: An instance of the appropriate derived type for the given view
        :rtype: :class:`~.view.View`
        """
        pluginxml = PluginXML(controller.config_xml)

        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                return plugin(controller, jenkins_master)

        raise PluginNotSupportedError("View plugin {0} not found".format(pluginxml.get_class_name()),
                                      pluginxml.get_class_name())

    @staticmethod
    def supported_types():
        """Returns a list of all view types supported by this instance of PyJen

        These view types can be used in such methods as :py:meth:`~.jenkins.Jenkins.create_view`, which take as input
        a view type classifier

        :return: list of all view types supported by this instance of PyJen, including those supported by plugins
        :rtype: :class:`list` of :class:`str`
        """
        retval = []
        from pyjen.view import View
        for plugin in get_plugins():
            if issubclass(plugin, View):
                retval.append(plugin.type)

        return retval

    @property
    def name(self):
        """Gets the display name for this view

        This is the name as it appears in the tabbed view
        of the main Jenkins dashboard

        :returns: the name of the view
        :rtype: :class:`str`
        """
        data = self._controller.get_api_data()
        return data['name']

    @property
    def contains_views(self):
        """Indicates whether this view type supports sub-views

        :returns: True if this type of view contains other views, False if not
        :rtype: :class:`bool`
        """
        return False

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
        data = self._controller.get_api_data()

        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:
            temp_data_io = self._controller.clone(j['url'])
            retval.append(Job.create(temp_data_io, self._master))

        return retval

    @property
    def _light_jobs(self):
        """Private helper method used to instantiate partial job classes for improved performance

        :returns: list of abstract jobs contained wthin this view
        :rtype: :class:`list` of :class:`str`
        """
        data = self._controller.get_api_data()
        retval = []
        for j in data['jobs']:
            temp_data_io = self._controller.clone(j['url'])
            retval.append(Job._create(temp_data_io, self._master, j['name']))

        return retval

    @property
    def job_count(self):
        """Gets the number of jobs contained under this view

        :returns: number of jobs contained under this view
        :rtype: :class:`int`
        """
        data = self._controller.get_api_data()

        return len(data['jobs'])

    @property
    def _job_names(self):
        """Gets the list of names of all jobs contained within this view

        :returns: the list of names of all jobs contained within this view
        :rtype: :class:`list` of :class:`str`
        """
        data = self._controller.get_api_data()
        retval = []
        for j in data['jobs']:
            retval.append(j['name'])
        return retval

    @property
    def _job_urls(self):
        """Gets the list of URLs for all jobs contained by this view
        :returns: the list of URLs for all jobs contained by this view
        :rtype: :class:`list` of :class:`str`
        """
        data = self._controller.get_api_data()
        retval = []
        for j in data['jobs']:
            retval.append(j['url'])
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
        return self._controller.config_xml

    @config_xml.setter
    def config_xml(self, new_xml):
        """Updates the raw configuration of this view with a new set of properties

        :param str new_xml:
            XML encoded text string to be used as a replacement for the
            current configuration being used by this view.

            NOTE: It is assumed that this input text meets the schema
            requirements for a Jenkins view.
        """
        self._controller.config_xml = new_xml

    def delete(self):
        """Deletes this view from the dashboard"""
        self._controller.post("/doDelete")

    def delete_all_jobs(self):
        """Batch method that allows callers to do bulk deletes of all jobs found in this view"""

        # TODO: Find a way to leverage the job URLs contained within the View API data to accelerate this process
        #   Maybe we could expose some static methods on the job() base class for doing deletes using an absolute URL
        #   Or maybe we could allow the instantiation of the job() base class for performing basic operations through
        #       the abstract interface, without needing to know the derived class we're using (and hence, avoid having
        #       to make an extra hit on the server for each job just to pull back the config.xml)
        # TODO: Apply this same pattern to other similar batch methods like disable_all_jobs

        for j in self._light_jobs:
            log.debug("Deleting job " + j.name)
            j.delete()

    def disable_all_jobs(self):
        """Batch method that allows caller to bulk-disable all jobs found in this view"""
        for j in self._light_jobs:
            log.debug("Disabling job " + j.name)
            j.disable()

    def enable_all_jobs(self):
        """Batch method that allows caller to bulk-enable all jobs found in this view"""
        # TODO: Give some thought to the repercussions of using 'light_jobs' here. For example, if a derived Job
        # class were to override the 'enable' function, it would not get called here. Maybe we don't care...
        for j in self._light_jobs:
            log.debug("Enabling job " + j.name)
            j.enable()

    def clone_all_jobs(self, source_job_name_regex, new_job_substring):
        """Batch-clones all jobs contained within this view

        :param str source_job_name_regex:
            pattern to use as a substitution rule when generating new names for cloned jobs. Substrings within the
            existing job names that match this pattern will be replaced by the given substitution string
        :param str new_job_substring:
            character string used to generate new job names for the clones of the existing jobs. The substring
            of an existing job that matches the given regex will be replaced by this new string to create the
            new job name for it's cloned counterpart.
        :returns: list of newly created jobs
        :rtype: :class:`list` of :class:`~.job.Job` objects
        """
        # TODO: Need to clarify that the input parameters here are not regular expressions.
        # Either that or we need to somehow add support for regexes here
        temp_jobs = self._light_jobs

        # Create a mapping table for names of jobs
        # TODO: Add a helper method to this class that gets the list of job names only. This doesn't require any
        #   hits on the server because the content is all within the config info for the view. This should improve
        #   the performance of this section of the code
        job_map = {}
        for j in temp_jobs:
            job_map[j.name] = j.name.replace(source_job_name_regex, new_job_substring)

        # clone all jobs, and update internal references
        retval = []
        count = 0
        tot = len(temp_jobs)
        for j in temp_jobs:
            count += 1
            orig_name = j.name
            log.info("Cloning job {0} of {1}: {2}".format(count, tot, orig_name))

            new_job = j.clone(job_map[orig_name])

            # update all internal references
            xml = new_job.config_xml
            for k in job_map.keys():
                xml = xml.replace(k, job_map[k])
            new_job.config_xml = xml

            retval.append(new_job)

        return retval

    def clone(self, new_view_name):
        """Make a copy of this view with the specified name

        :param str new_view_name: name of the newly cloned view
        :return: reference to the View object that manages the new, cloned view
        :rtype: :class:`~.view.View`
        """
        v = self._master.create_view(new_view_name, self.type)
        vxml = ViewXML(self.config_xml)
        vxml.rename(new_view_name)
        v.config_xml = vxml.XML
        return v

    def rename(self, new_name):
        """Rename this view

        :param str new_name: new name for this view
        """
        new_view = self.clone(new_name)
        self.delete()
        self._controller = new_view._controller

if __name__ == "__main__":  # pragma: no cover

    for i in View.supported_types():
        print(i)
    pass
