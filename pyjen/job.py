from build import build
from pyjen.utils.job_xml import job_xml
from utils.data_requester import data_requester

class job(object):
    def __init__ (self, url, user=None, password=None):
        """Constructor
        
        Parameters
        ----------
        url : string
            root URL of the job being managed by this object
            Example: 'http://jenkins/jobs/job1'
        user : string
            optional user name to authenticate to Jenkins dashboard
        password : string
            password for Jenkins login credentials 
            if a user name is provided this parameter must be defined as well
        """
        if (user != None):
            assert (password != None)

        self.__url = url
        self.__requester = data_requester(url, user, password)
        
        
    def get_name(self):
        """Returns the name of the job managed by this object
        
        Returns
        -------
        string
            The name of the job
        """        
        data = self.__requester.get_data('/api/python')
        
        return data['name']
    
    def get_url(self):
        """Gets the full URL for the main web page for this job
        
        Return
        ------
        string
            URL of the main web page for the job
        """
        return self.__url
    
    def get_recent_builds(self):
        """Gets a list of the most recent builds for this job
        
        Rather than returning all data on all available builds, this
        method only returns the latest 20 or 30 builds. This list is
        synonymous with the short list provided on the main info
        page for the job on the dashboard.
        """
        data = self.__requester.get_data('/api/python')
        
        builds = data['builds']
        
        retval = []
        for b in builds:
            retval.append(build(b['url']))
        
        return retval
    
    def get_downstream_jobs(self):
        """Gets the list of immediate downstream dependencies for this job
        
        Returns
        -------
        pyjen.job
            A list of 0 or more jobs which depend on this one
        """
        data = self.__requester.get_data('/api/python')
        
        jobs = data['downstreamProjects']
        
        retval = []
        for j in jobs:
            retval.append(job(j['url']))
        
        return retval
    
    def get_upstream_jobs(self):
        """Gets the list of immediate upstream dependencies for this job
        
        Returns
        -------
        pyjen.job
            A list of 0 or more jobs that this job depends on
        """
        data = self.__requester.get_data('/api/python')
        
        jobs = data['upstreamProjects']
        
        retval = []
        for j in jobs:
            retval.append(job(j['url']))
        
        return retval
    
    def get_last_good_build(self):
        """Gets the most recent successful build of this job
        
        Synonymous with the last good build permalink on the jobs main dashboard
        
        Return
        ------
        pyjen.build
            object that provides information and control for the
            last build which completed with a status of 'success'
        """
        data = self.__requester.get_data('/api/python')
        
        lgb = data['lastSuccessfulBuild']
        
        return build(lgb['url'])
        
    def get_last_build(self):
        """Returns a reference to the most recent build of this job
        
        Return
        ------
        pyjen.build
            object that provides information and control for the
            most recent build of this job.
        """
        data = self.__requester.get_data('/api/python')
        
        last_build = data['lastBuild']
        
        return build (last_build['url'])
                
    def start_build(self):
        """Forces a build of this job
        
        Synonymous with a manual trigger. A new instance
        of the job (ie: a build) will be added to the
        appropriate build queue where it will be scheduled
        for execution on the next available agent + executor.
        """
        self.__requester.post("/build")
        
    def disable(self):
        """Disables this job
        
        Sets the state of this job to disabled so as to prevent the 
        job from being triggered.
        
        Use in conjunction with the enable() and is_disabled()
        methods to control the state of the job.
        """
        self.__requester.post("/disable")
        
    def enable(self):
        """Enables this job
        
        If this jobs current state is disabled, it will be
        re-enabled after calling this method. If the job
        is already enabled then this method does nothing.
        
        Enabling a job allows it to be triggered, either automatically
        via commit hooks / polls or manually through the dashboard.
        
        Use in conjunction with the disable() and is_disabled() methods
        """
        self.__requester.post("/enable")
        
    def is_disabled(self):
        """Indicates whether this job is disabled or not
        
        Returns
        -------
        boolean
            true if the job is disabled, otherwise false
        """
        data = self.__requester.get_data('/api/python')
        
        return (data['color'] == "disabled")
        
        
    def delete (self):
        """Deletes this job from the Jenkins dashboard"""
        self.__requester.post("/doDelete")
        
    def get_config_xml(self):
        """Gets the raw XML configuration for the job
        
        Used in conjunction with the set_config_xml method,
        callers are free to manipulate the raw job configuration
        as desired.
        
        Returns
        -------
        string
            the full XML tree describing this jobs configuration
        """
        return self.__requester.get_text('/config.xml')
    
    def set_config_xml(self, new_xml):
        """Allows a caller to manually override the entire job configuration
        
        WARNING: This is an advanced method that should only be used in
        rare circumstances. All configuration changes should normally
        be handled using other methods provided on this class.
        
        Parameters
        ----------
        new_xml : string
            A complete XML tree compatible with the Jenkins API
        """
        headers = {'Content-Type': 'text/xml'}
        args = {}
        args['data'] = new_xml
        args['headers'] = headers
        
        self.__requester.post("/config.xml", **args)
        
    def set_custom_workspace(self, path):
        """Defines a new custom workspace for the job
        
        If this job is already using a custom workspace it
        will be updated to the new path provided.
        
        Parameters
        ----------
        path : string
            new custom workspace path
        """
        xml = self.get_config_xml()
        
        jobxml = job_xml(xml)
        jobxml.set_custom_workspace(path)
        
        self.set_config_xml(jobxml.get_xml())
        
    def get_scm(self):
        """Gets the object that manages the source code management configuration for a job
        
        Returns
        -------
        object
            One of several possible plugin objects which exposes the relevant set
            of properties supported by a given source code management tool.
            
        """
        xml = self.get_config_xml()
        jobxml = job_xml(xml)
        return jobxml.get_scm()
        
        
        
if __name__ == "__main__":
    j = job("http://localhost:8080/job/test_job")
    print j.get_name()
    scm = j.get_scm()

    mods = scm.get_modules()
    print len(mods)
    print mods

    
    