"""Primitives that manage Jenkins job of type 'Folder'"""
from pyjen.job import Job
from pyjen.utils.helpers import create_job


class FolderJob(Job):
    """Jenkins job of type 'folder'"""
    @property
    def jobs(self):
        """Gets a list of all jobs contained in this folder

        :rtype: :class:`list` of :class:`~.job.Job`
        """
        data = self._api.get_api_data()

        retval = list()
        for tjob in data['jobs']:
            retval.append(Job.instantiate(tjob, self._api))

        return retval

    def create_job(self, job_name, job_class):
        """Creates a new job on the Jenkins dashboard

        :param str job_name:
            the name for this new job
            This name should be unique, different from any other jobs currently
            managed by the Jenkins instance
        :param job_class:
            PyJen plugin class associated with the type of job to be created
        :returns: An object to manage the newly created job
        :rtype: :class:`~.job.Job`
        """
        create_job(self._api, job_name, job_class)
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

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def template_config_xml():
        """XML configuration template for  instantiating jobs of this type

        :returns:
            a basic XML configuration template for use when instantiating
            jobs of this type
        :rtype: :class:`str`
        """
        xml = """
<com.cloudbees.hudson.plugins.folder.Folder>
    <description/>
    <properties>
        <org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
            <dockerLabel/>
            <registry/>
        </org.jenkinsci.plugins.pipeline.modeldefinition.config.FolderConfig>
    </properties>
    <folderViews 
      class="com.cloudbees.hudson.plugins.folder.views.DefaultFolderViewHolder">
        <views>
            <hudson.model.AllView>
                <owner class="com.cloudbees.hudson.plugins.folder.Folder" 
                  reference="../../../.."/>
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


PluginClass = FolderJob


if __name__ == "__main__":  # pragma: no cover
    pass
