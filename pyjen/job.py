from pyjen.build import build
from pyjen.utils.job_xml import job_xml
from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError

class job(object):
    """Interface to all primitives associated with a Jenkins job"""
    
    def __init__ (self, data_io_controller):
        """Constructor
        
        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method
        
        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API        
        """
        self.__data_io = data_io_controller
        
    @staticmethod
    def easy_connect(url, credentials=None):
        """Factory method to simplify creating connections to Jenkins servers
        
        :param str url: Full URL of the Jenkins instance to connect to. Must be a valid job on a valid Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and password for authenticating to the URL
            If no credentials can be found elsewhere, anonymous access will be chosen
        :returns: :py:mod:`pyjen.job` object, pre-configured with the appropriate credentials
            and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.job`
        """
        if credentials != None:
            username = credentials[0]
            password = credentials[1]
        else:
            username = ""
            password = ""
        
        http_io = data_requester(url, username, password)
        retval = job(http_io)
        
        # Sanity check: make sure we can successfully parse the view's name from the IO controller to make sure
        # we have a valid configuration
        try:
            name = retval.get_name()
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Job. Please check configuration.", http_io) 
        if name == None or name == "":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Job. Please check configuration.", http_io) 
    
        return retval
        
    def get_name(self):
        """Returns the name of the job managed by this object
        
        :returns: The name of the job
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()      
        return data['name']
    
    def start_build(self):
        """Forces a build of this job
        
        Synonymous with a manual trigger. A new instance
        of the job (ie: a build) will be added to the
        appropriate build queue where it will be scheduled
        for execution on the next available agent + executor.
        """
        self.__data_io.post("/build")
        
    def disable(self):
        """Disables this job
        
        Sets the state of this job to disabled so as to prevent the 
        job from being triggered.
        
        Use in conjunction with the :py:func:`enable` and :py:func:`is_disabled`
        methods to control the state of the job.
        """
        self.__data_io.post("/disable")
        
    def enable(self):
        """Enables this job
        
        If this jobs current state is disabled, it will be
        re-enabled after calling this method. If the job
        is already enabled then this method does nothing.
        
        Enabling a job allows it to be triggered, either automatically
        via commit hooks / polls or manually through the dashboard.
        
        Use in conjunction with the :py:func:`disable` and :py:func:`is_disabled` methods
        """
        self.__data_io.post("/enable")
        
    def is_disabled(self):
        """Indicates whether this job is disabled or not
        
        :returns:
            true if the job is disabled, otherwise false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()
        
        return (data['color'] == "disabled")
        
        
    def delete (self):
        """Deletes this job from the Jenkins dashboard"""
        self.__data_io.post("/doDelete")
        
    
    def has_been_built(self):
        """Checks to see whether this job has ever been built or not
        
        :returns: True if the job has been built at least once, otherwise false
        :rtype: :py:module:`bool`
        """
        
        data = self.__data_io.get_api_data()
        
        return (data['color'] != "notbuilt")
    
    def get_downstream_jobs(self, recursive=False):
        """Gets the list of jobs to be triggered after this job completes
        
        :param bool recursive:
            Set to True to recursively scan all downstream jobs
            for their downstream dependencies and return the complete
            list of all dependencies
            
            Set to False to only report the immediate downstream
            dependencies - those directly triggered by this job.
            
            Defaults to False
        :returns: 
            A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :py:mod:`pyjen.job` objects
        """
        data = self.__data_io.get_api_data()
        
        jobs = data['downstreamProjects']
        
        retval = []
        
        for j in jobs:
            temp_data_io = self.__data_io.clone(j['url'])
            temp_job = job(temp_data_io)
            retval.append(temp_job)
            if recursive:
                retval.extend(temp_job.get_downstream_jobs(recursive))
        
        return retval
    
    def get_upstream_jobs(self, recursive=False):
        """Gets the list of upstream dependencies for this job
        
        :param bool recursive:
            Set to True to recursively scan all upstream jobs
            for their upstream dependencies and return the complete
            list of all dependencies
            
            Set to False to only report the immediate upstream
            dependencies - those that directly trigger this job.
            
            Defaults to False
            
        :returns:
            A list of 0 or more jobs that this job depends on
        :rtype: :class:`list` of :py:mod:`pyjen.job` objects
        """
        data = self.__data_io.get_api_data()
        
        jobs = data['upstreamProjects']
        
        retval = []
                
        for j in jobs:
            temp_data_io = self.__data_io.clone(j['url'])
            temp_job = job(temp_data_io)
            retval.append(temp_job)
            if recursive:
                retval.extend(temp_job.get_upstream_jobs(recursive))
        
        return retval    
        
    def get_recent_builds(self):
        """Gets a list of the most recent builds for this job
        
        Rather than returning all data on all available builds, this
        method only returns the latest 20 or 30 builds. This list is
        synonymous with the short list provided on the main info
        page for the job on the dashboard.
        
        :rtype: :func:`list` of :py:mod:`pyjen.build` objects
        """
        data = self.__data_io.get_api_data()
        
        builds = data['builds']
        
        retval = []
        for b in builds:
            temp_data_io = self.__data_io.clone(b['url'])
            temp_build = build(temp_data_io)
            retval.append(temp_build)
        
        return retval
    
    def get_last_good_build(self):
        """Gets the most recent successful build of this job
        
        Synonymous with the "Last successful build" permalink on the jobs' main status page
        
        
        :returns:
            object that provides information and control for the
            last build which completed with a status of 'success'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.build`
        """
        data = self.__data_io.get_api_data()
        
        lgb = data['lastSuccessfulBuild']
        
        if lgb == None:
            return None
        
        temp_data_io = self.__data_io.clone(lgb['url'])
        return build(temp_data_io)
        
    def get_last_build(self):
        """Returns a reference to the most recent build of this job
        
        Synonymous with the "Last Build" permalink on the jobs' main status page
        
        :returns:
            object that provides information and control for the
            most recent build of this job.
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.build`
        """
        data = self.__data_io.get_api_data()
        
        last_build = data['lastBuild']
        
        if last_build == None:
            return None
        
        temp_data_io = self.__data_io.clone(last_build['url'])
        return build (temp_data_io)
    
    def get_last_failed_build(self):
        """Returns a reference to the most recent build of this job with a status of "failed"
        
        Synonymous with the "Last failed build" permalink on the jobs' main status page
        
        :returns:
            Most recent build with a status of 'failed'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.build`
        """
        data = self.__data_io.get_api_data()
        
        bld = data['lastFailedBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return build(temp_data_io)
                
    def get_last_stable_build(self):
        """Returns a reference to the most recent build of this job with a status of "stable"
        
        Synonymous with the "Last stable build" permalink on the jobs' main status page
        
        
        :returns:
            Most recent build with a status of 'stable'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.build`
        """
        data = self.__data_io.get_api_data()

        bld = data['lastCompletedBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return build(temp_data_io)
    
    def get_last_unsuccessful_build(self):
        """Returns a reference to the most recent build of this job with a status of "unstable"
        
        Synonymous with the "Last unsuccessful build" permalink on the jobs' main status page
        
        :returns:
            Most recent build with a status of 'unstable'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.build`
        """
        data = self.__data_io.get_api_data()

        bld = data['lastUnsuccessfulBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return build(temp_data_io)    
        
    def get_build_by_number(self, build_number):
        """Gets a specific build of this job from the build history
        
        :param int build_number:
            Numeric identifier of the build to retrieve
            Value is typically non-negative
        :returns:
            Build object for the build with the given numeric identifier
            If such a build does not exist, returns None
        :rtype: :py:mod:`pyjen.build`
        """
        temp_data_io = self.__data_io.clone(self.__data_io.url + "/" + str(build_number))

        # Lets try loading data from the given URL to see if it is valid. 
        # If it's not valid we'll assume a build with the given number doesn't exist 
        try:
            temp_data_io.get_api_data()
        except AssertionError:
            return None
        
        return build(temp_data_io)
    
    def get_builds_in_time_range(self, startTime, endTime):
        """ Returns a list of all of the builds for a job that 
            occurred between the specified start and end times
            
            :param datetime startTime: 
                    starting time index for range of builds to find
            :param datetime endTime:
                    ending time index for range of builds to find
            :returns: a list of 0 or more builds
            :rtype: :class:`list` of :py:mod:`pyjen.build` objects            
        """       
        if startTime > endTime:
            tmp = endTime
            endTime = startTime
            startTime = tmp
            
        builds = []                
        
        for run in self.get_recent_builds():            
            if (run.get_build_time() < startTime):
                break
            elif (run.get_build_time() >= startTime and run.get_build_time() <= endTime):
                builds.append(run)                               
        return builds
        
    def get_config_xml(self):
        """Gets the raw XML configuration for the job
        
        Used in conjunction with the set_config_xml method,
        callers are free to manipulate the raw job configuration
        as desired.
        
        :returns:
            the full XML tree describing this jobs configuration
        :rtype: :func:`str`
        """
        return self.__data_io.get_text('/config.xml')
    
    def set_config_xml(self, new_xml):
        """Allows a caller to manually override the entire job configuration
        
        WARNING: This is an advanced method that should only be used in
        rare circumstances. All configuration changes should normally
        be handled using other methods provided on this class.
        
        :param str new_xml:
            A complete XML tree compatible with the Jenkins API
        """
        headers = {'Content-Type': 'text/xml'}
        args = {}
        args['data'] = new_xml
        args['headers'] = headers
        
        self.__data_io.post("/config.xml", args)
        
    def set_custom_workspace(self, path):
        """Defines a new custom workspace for the job
        
        If this job is already using a custom workspace it
        will be updated to the new path provided.
        
        :param str path: new custom workspace path
        """
        xml = self.get_config_xml()
        
        jobxml = job_xml(xml)
        jobxml.set_custom_workspace(path)
        
        self.set_config_xml(jobxml.get_xml())
        
    def get_scm(self):
        """Gets the object that manages the source code management configuration for a job
        
        :returns:
            One of several possible plugin objects which exposes the relevant set
            of properties supported by a given source code management tool.
        :rtype: :py:class:`pyjen.plugins.pluginbase`    
        """
        xml = self.get_config_xml()
        jobxml = job_xml(xml)
        return jobxml.get_scm()

if __name__ == "__main__":
    pass