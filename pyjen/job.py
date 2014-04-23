from pyjen.build import build
from pyjen.utils.job_xml import job_xml
from pyjen.utils.data_requester import data_requester
from pyjen.utils.common import get_root_url

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
    
    def get_authenticated_user(self):
        """Gets the user name portion of the credentials used to access this view
        
        See also: get_authenticated_password
        
        Return
        ------
        string
            the user name used to authenticate transactions with this view
        """
        return self.__requester.get_user()
    
    def get_authenticated_password(self):
        """Gets the password portion of the credentials used to access this view
        
        See also: get_authenticated_user
        
        Return
        ------
        string
            the password used to authenticate transactions with this view
        """
        return self.__requester.get_password()
    
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
    
    def get_downstream_jobs(self, recursive=False):
        """Gets the list of immediate downstream dependencies for this job
        
        Parameters
        ----------
        recursive : boolean
            Set to True to recursively scan all downstream jobs
            for their downstream dependencies and return the complete
            list of all dependencies
            
            Set to False to only report the immediate downstream
            dependencies - those directly triggered by this job.
            
            Defaults to False
            
        Returns
        -------
        dictionary{job_name, pyjen.job}
            A dictionary of 0 or more jobs which depend on this one
            the keys in the dictionary are the names of the jobs that
            were found in the dependency search
        """
        data = self.__requester.get_data('/api/python')
        
        jobs = data['downstreamProjects']
        
        retval = {}
        
        
        for j in jobs:
            temp = job(j['url'])
            retval[temp.get_name()] = temp
            if recursive:
                retval.update(temp.get_downstream_jobs(recursive))
        
        return retval
    
    def get_upstream_jobs(self, recursive=False):
        """Gets the list of upstream dependencies for this job
        
        Parameters
        ----------
        recursive : boolean
            Set to True to recursively scan all upstream jobs
            for their upstream dependencies and return the complete
            list of all dependencies
            
            Set to False to only report the immediate upstream
            dependencies - those that directly trigger this job.
            
            Defaults to False
            
        Returns
        -------
        dictionary{job_name, pyjen.job}
            A dictionary of 0 or more jobs that this job depends on
            the keys in the dictionary are the names of the jobs that
            were found in the dependency search
        """
        data = self.__requester.get_data('/api/python')
        
        jobs = data['upstreamProjects']
        
        retval = {}
                
        for j in jobs:
            temp = job(j['url'])
            retval[temp.get_name()] = temp
            if recursive:
                retval.update(temp.get_upstream_jobs(recursive))
        
        return retval    
        
    def get_last_good_build(self):
        """Gets the most recent successful build of this job
        
        Synonymous with the "Last successful build" permalink on the jobs' main status page
        
        Return
        ------
        pyjen.build
            object that provides information and control for the
            last build which completed with a status of 'success'
            If there are no such builds in the build history, this method returns None
        """
        data = self.__requester.get_data('/api/python')
        
        lgb = data['lastSuccessfulBuild']
        
        if lgb == None:
            return None
        
        return build(lgb['url'])
        
    def get_last_build(self):
        """Returns a reference to the most recent build of this job
        
        Synonymous with the "Last Build" permalink on the jobs' main status page
        
        Return
        ------
        pyjen.build
            object that provides information and control for the
            most recent build of this job.
            If there are no such builds in the build history, this method returns None
        """
        data = self.__requester.get_data('/api/python')
        
        last_build = data['lastBuild']
        
        if last_build == None:
            return None
        
        return build (last_build['url'])
    
    def get_last_failed_build(self):
        """Returns a reference to the most recent build of this job with a status of "failed"
        
        Synonymous with the "Last failed build" permalink on the jobs' main status page
        
        Returns
        -------
        pyjen.build
            Most recent build with a status of 'failed'
            If there are no such builds in the build history, this method returns None
        """
        data = self.__requester.get_data('/api/python')
        
        bld = data['lastFailedBuild']
        
        if bld == None:
            return None
        
        return build(bld['url'])
                
    def get_last_stable_build(self):
        """Returns a reference to the most recent build of this job with a status of "stable"
        
        Synonymous with the "Last stable build" permalink on the jobs' main status page
        
        Returns
        -------
        pyjen.build
            Most recent build with a status of 'stable'
            If there are no such builds in the build history, this method returns None
        """
        data = self.__requester.get_data('/api/python')

        bld = data['lastCompletedBuild']
        
        if bld == None:
            return None
        
        return build(bld['url'])
    
    def get_last_unsuccessful_build(self):
        """Returns a reference to the most recent build of this job with a status of "unstable"
        
        Synonymous with the "Last unsuccessful build" permalink on the jobs' main status page
        
        Returns
        -------
        pyjen.build
            Most recent build with a status of 'unstable'
            If there are no such builds in the build history, this method returns None
        """
        data = self.__requester.get_data('/api/python')

        bld = data['lastUnsuccessfulBuild']
        
        if bld == None:
            return None
        
        return build(bld['url'])    
        
    def get_build_by_number(self, build_number):
        """Gets a specific build of this job from the build history
        
        Parameters
        ----------
        build_number : integer
            Numeric identifier of the build to retrieve
            Value is typically non-negative
            
        Return
        ------
        pyjen.build
            Build object for the build with the given numeric identifier
            If such a build does not exist, returns None
        """
        try:
            data = self.__requester.get_data("/" + str(build_number)  + "/api/python")
        except AssertionError:
            #TODO: Find a more elegant way to detect whether the build exists or not
            return None
        
        return build(data['url'])
    
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
        
        self.__requester.post("/config.xml", args)
        
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

    def get_builds_in_time_range(self, startTime, endTime):
        """ Returns a list of all of the builds for a job that 
            occurred between the specified start and end times
            
            Parameters
            ----------
                startTime 
                    datetime object representing the ceiling of the range
                endTime
                    datetime object representing the floor of the range
            Returns
            -------
                List[build]
                    a list of builds            
        """       
        builds = []                
        
        for run in self.get_recent_builds():            
            if (run.get_build_time() < startTime):
                break
            elif (run.get_build_time() >= startTime and run.get_build_time() <= endTime):
                builds.append(run)                               
        return builds
        
    def clone(self, new_job_name):
        """Makes a copy of this job on the dashboard with a new name        
        
        Parameters
        ----------            
        new_job_name : string
            the name of the newly created job whose settings will
            be an exact copy of this job. It is expected that this
            new job name be unique across the dashboard.
            
        Returns
        -------
        pyjen.job
            returns a reference to the newly created job resulting
            from the clone operation
        """
        
        params = {'name': new_job_name,
                  'mode': 'copy',
                  'from': self.get_name()}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
        args = {}
        args['params'] = params
        args['data'] = ''
        args['headers'] = headers
        
        dashboard_url = get_root_url(self.get_url())
        self.__requester.post_url(dashboard_url + "/createItem", args)
        
        new_job_url = dashboard_url + "/job/" + new_job_name + "/"
        new_job = job(new_job_url, self.__requester.get_user(), self.__requester.get_password())
        
        # Sanity check - lets make sure the job actually exists by checking its name
        assert(new_job.get_name() == new_job_name)
        
        #as a precaution, lets disable the newly created job so it doesn't automatically start running
        new_job.disable()
        
        return new_job 
        
if __name__ == "__main__":
    j = job("http://localhost:8080/job/test_job/")
    j.clone('new_job_name')
    #print j2.get_config_xml()
    #j.clone_job("ksp_generated_subjob")
    #print j.get_name()