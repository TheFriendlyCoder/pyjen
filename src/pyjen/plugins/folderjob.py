"""Primitives that manage Jenkins job of type 'Folder'"""
from pyjen.job import Job
from pyjen.utils.plugin_api import find_plugin
from pyjen.exceptions import PluginNotSupportedError


class FolderJob(Job):
    """Jenkins job of type 'folder'

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(FolderJob, self).__init__(api)

    @staticmethod
    def template_config_xml():
        """XML configuration template for  instantiating jobs of this type

        :returns:
            a basic XML configuration template for use when instantiating
            jobs of this type
        :rtype: :class:`str`
        """
        xml = """<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@6.7">
    <description/>
    <properties>
        <org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig plugin="pipeline-model-definition@1.3.6">
        <dockerLabel/>
        <registry plugin="docker-commons@1.13"/>
        </org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
    </properties>
    <folderViews class="com.cloudbees.hudson.plugins.folder.views.DefaultFolderViewHolder">
        <views>
            <hudson.model.AllView>
                <owner class="com.cloudbees.hudson.plugins.folder.Folder" reference="../../../.."/>
                <name>All</name>
                <filterExecutors>false</filterExecutors>
                <filterQueue>false</filterQueue>
                <properties class="hudson.model.View$PropertyList"/>
            </hudson.model.AllView>
        </views>
        <tabBar class="hudson.views.DefaultViewsTabBar"/>
    </folderViews>
    <healthMetrics>
        <com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
            <nonRecursive>false</nonRecursive>
        </com.cloudbees.hudson.plugins.folder.health.WorstChildHealthMetric>
    </healthMetrics>
    <icon class="com.cloudbees.hudson.plugins.folder.icons.StockFolderIcon"/>
</com.cloudbees.hudson.plugins.folder.Folder>"""
        return xml

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "com.cloudbees.hudson.plugins.folder.Folder"

    def create_job(self, job_name, job_type):
        """Creates a new job on the Jenkins dashboard

        :param str job_name:
            the name for this new job
            This name should be unique, different from any other jobs currently
            managed by the Jenkins instance
        :param str job_type:
            type of job to create
            must match one or more of the available jenkins types supported by
            this Jenkins instance.
            See :py:meth:`~.job.Job.supported_types` for a list of
            supported job types.
        :returns: An object to manage the newly created job
        :rtype: :class:`~.job.Job`
        """
        job_type = job_type.replace("__", "_")

        headers = {'Content-Type': 'text/xml'}

        params = {
            "name": job_name
        }

        plugin = find_plugin(job_type)
        if plugin is None:
            raise PluginNotSupportedError(
                "Attempting to create a new job with an unsupported format",
                job_type)
        xml_config = plugin.template_config_xml()
        data = xml_config

        args = {
            'data': data,
            'params': params,
            'headers': headers
        }

        self._api.post(self._api.url + 'createItem', args)

        retval = self.find_job(job_name)
        assert retval is not None
        return retval

    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job

        .. seealso: :py:meth:`.get_job`

        :param str job_name: the name of the job to search for
        :returns:
            If a job with the specified name can be found, and object to manage
            the job will be returned, otherwise None
        :rtype: :class:`~.job.Job`
        """
        data = self._api.get_api_data()
        tjobs = data['jobs']

        for tjob in tjobs:
            if tjob['name'] == job_name:
                return Job.instantiate(tjob, self._api)

        return None

    def clone_job(self, source_job, new_job_name, disable=True):
        """"Create a new job with the same configuration as this one

        :param source_job: job to be cloned
        :type source_job: :class:`pyjen.job.Job`
        :param str new_job_name: Name of the new job to be created
        :param bool disable:
            Indicates whether the newly created job should be disabled after
            creation to prevent builds from accidentally triggering
            immediately after creation
        :returns: reference to the newly created job
        :rtype: :class:`pyjen.job.Job`
        """
        # Try to extract the plugin name from a static helper method from
        # the PyJen plugin to avoid having to hit the REST API for it. If
        # we don't have a PyJen plugin to query, then we fall back to the
        # jenkins_plugin_name property which has to call out to the REST API,
        # which is slower
        if hasattr(source_job, "get_jenkins_plugin_name"):
            plugin_name = source_job.get_jenkins_plugin_name()
        else:
            plugin_name = source_job.jenkins_plugin_name

        # create a new job with the specified name and then copy the
        # configuration from the old job to the new one
        new_job = self.create_job(
            new_job_name, plugin_name)
        new_job.config_xml = source_job.config_xml

        if disable:
            new_job.disable()
        return new_job

    def move_job(self, existing_job):
        """Moves an existing job under this folder job

        NOTE: The original job object becomes obsolete after executing this
        operation

        :param existing_job: Instance of a PyJen job to be moved
        :type existing_job: :class:`pyjen.job.Job`
        :returns: reference to new, relocated job object
        :rtype: :class:`pyjen.job.Job`
        """
        # Try to extract the plugin name from a static helper method from
        # the PyJen plugin to avoid having to hit the REST API for it. If
        # we don't have a PyJen plugin to query, then we fall back to the
        # jenkins_plugin_name property which has to call out to the REST API,
        # which is slower
        if hasattr(existing_job, "get_jenkins_plugin_name"):
            plugin_name = existing_job.get_jenkins_plugin_name()
        else:
            plugin_name = existing_job.jenkins_plugin_name

        new_job = self.create_job(
            existing_job.name, plugin_name)
        new_job.config_xml = existing_job.config_xml
        existing_job.delete()
        return new_job


PluginClass = FolderJob


if __name__ == "__main__":  # pragma: no cover
    pass
