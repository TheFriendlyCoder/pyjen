"""Primitives for interacting with Jenkins views"""
from pyjen.job import Job
from pyjen.exceptions import NotYetImplementedError
import xml.etree.ElementTree as ElementTree
import pyjen.utils.pluginapi as pluginapi


class View(object):
    """ 'Abstract' base class used by all view classes, providing functionality common to them all"""

    def __init__(self, data_io_controller, jenkins_master):
        """Constructor

        :param obj data_io_controller: IO interface which manages interaction with the live Jenkins view
        :param obj jenkins_master: Instance of the :py:mod:`pyjen.Jenkins` class this view belongs to
        """
        self._controller = data_io_controller
        self._master = jenkins_master

    @staticmethod
    def create(controller, jenkins_master):
        """Factory method used to instantiate the appropriate view type for a given configuration

        :param obj controller: IO interface to the Jenkins API. This object is expected to be pre-initialized
            with the connection parameters for the view to be processed.
        :param obj jenkins_master: Instance of the :py:mod:`pyjen.Jenkins` class this view belongs to
        :return: An instance of the appropriate derived type for the given view
        :rtype: :py:mod:`pyjen.View`
        """

        # NOTE: We need to import the classes to instantiate from inside this function
        #       to prevent circular dependencies between these and the current class
        from pyjen.listview import ListView
        from pyjen.allview import AllView
        from pyjen.myview import MyView

        config = controller.get_text('/config.xml')
        root = ElementTree.fromstring(config)

        if root.tag == "hudson.model.ListView":
            return ListView(controller, jenkins_master)

        if root.tag == "hudson.model.AllView":
            return AllView(controller, jenkins_master)

        if root.tag == "hudson.model.MyView":
            return MyView(controller, jenkins_master)

        return pluginapi.find_view_plugin(config)(controller, jenkins_master)

    @staticmethod
    def supported_types():
        """Returns a list of all view types supported by this instance of PyJen

        These view types can be used in such methods as :py:meth:`pyjen.Jenkins.create_view`, which take as input
        a view type classifier

        :return: list of all view types supported by this instance of PyJen, including those supported by plugins
        :rtype: :func:`str`
        """
        retval = []

        # built in types
        retval.append("hudson.model.ListView")
        retval.append("hudson.model.AllView")
        retval.append("hudson.model.MyView")

        # types supported by plugins
        for plugin in pluginapi.get_view_plugins():
            retval.append(plugin.type)

        return retval

    @property
    def name(self):
        """Gets the display name for this view

        This is the name as it appears in the tabed view
        of the main Jenkins dashboard

        :returns: the name of the view
        :rtype: :func:`str`
        """
        data = self._controller.get_api_data()
        return data['name']

    @property
    def contains_views(self):
        """Indicates whether this view type supports sub-views
        :rtype: :func:`bool`
        """
        return False

    @property
    def jobs (self):
        """Gets a list of jobs associated with this view

        Views are simply filters to help organize jobs on the
        Jenkins dashboard. This method returns the set of jobs
        that meet the requirements of the filter associated
        with this view.

        :returns: list of 0 or more jobs that are included in this view
        :rtype:  :class:`list` of :py:mod:`pyjen.Job` objects
        """
        data = self._controller.get_api_data()

        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:
            temp_data_io = self._controller.clone(j['url'])
            retval.append(Job.create(temp_data_io, self._master))

        return retval

    @property
    def job_count(self):
        """Gets the number of jobs contained under this view

        :returns: number of jobs contained under this view
        :rtype: :func:`int`
        """
        data = self._controller.get_api_data()

        return len(data['jobs'])

    @property
    def config_xml(self):
        """Gets the raw configuration data in XML format

        This is an advanced function which allows the caller
        to manually manipulate the raw configuration settings
        of the view. Use with caution.

        This method can be used in conjunction with the
        :py:func:`pyjen.View.set_config_xml` method to dynamically
        update arbitrary properties of this view.

        :returns:
            returns the raw XML of the views configuration in
            a plain text string format
        :rtype: :func:`str`
        """
        return self._controller.get_text("/config.xml")

    def set_config_xml(self, new_xml):
        """Updates the raw configuration of this view with a new set of properties

        This method should typically used in conjunction with
        the :py:func:`pyjen.View.get_config_xml` method.

        :param str new_xml:
            XML encoded text string to be used as a replacement for the
            current configuration being used by this view.

            NOTE: It is assumed that this input text meets the schema
            requirements for a Jenkins view.
        """
        headers = {'Content-Type': 'text/xml'}
        args = {}
        args['data'] = new_xml
        args['headers'] = headers

        self._controller.post("/config.xml", args)

    def delete(self):
        """Deletes this view from the dashboard"""
        self._controller.post("/doDelete")

    def delete_all_jobs(self):
        """Helper method that allows callers to do bulk deletes of all jobs found in this view"""

        my_jobs = self.jobs
        for j in my_jobs:
            j.delete()

    def disable_all_jobs(self):
        """Helper method that allows caller to bulk-disable all jobs found in this view"""
        my_jobs = self.jobs
        for j in my_jobs:
            j.disable()

    def enable_all_jobs(self):
        """Helper method that allows caller to bulk-enable all jobs found in this view"""
        my_jobs = self.jobs
        for j in my_jobs:
            j.enable()

    def clone_all_jobs(self, source_job_name_regex, new_job_substring):
        """Helper method that does a batch clone on all jobs found in this view
        :param str source_job_name_regex: pattern to use as a substitution rule
            when generating new names for cloned jobs. Substrings within the
            existing job names that match this pattern will be replaced by
            the given substitution string
        :param str new_job_substring: character string used to
            generate new job names for the clones of the existing jobs. The substring
            of an existing job that matches the given regex will be replaced by this
            new string to create the new job name for it's cloned counterpart.
        :returns: list of newly created jobs
        :rtype: :class:`list` of :py:mod:`pyjen.Job` objects
        """
        temp_jobs = self.jobs

        # Create a mapping table for names of jobs
        job_map = {}
        for j in temp_jobs:
            orig_name = j.name
            job_map[orig_name] = orig_name.replace(source_job_name_regex, new_job_substring)

        # clone all jobs, and update internal references
        retval = []
        for j in temp_jobs:
            orig_name = j.name
            new_job = j.clone(job_map[orig_name])

            # update all internal references
            xml = new_job.config_xml
            for k in job_map.keys():
                xml = xml.replace(k, job_map[k])
            new_job.set_config_xml(xml)

            retval.append(new_job)

        return retval

    @property
    def type(self):
        """Retrieves the Jenkins view data type from this class instance

        Base classes are expected to define a 'static' property named after this method
        :rtype: :func:`str`
        """
        raise NotYetImplementedError()

    def clone(self, new_view_name):
        """Make a copy of this view with the specified name

        :param str new_view_name: name of the newly cloned view
        :return: reference to the PyJen View object that manages the new, cloned view
        :rtype: :py:mod:`pyjen.View`
        """
        v = self._master.create_view(new_view_name, self.type)
        v.set_config_xml (self.config_xml)
        return v

if __name__ == "__main__":  # pragma: no cover
    pass
