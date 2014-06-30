"""Primitives for interacting with Jenkins jobs"""
from pyjen.build import Build
from pyjen.utils.job_xml import job_xml
from pyjen.utils.data_requester import data_requester
from pyjen.exceptions import InvalidJenkinsURLError
from pyjen.user_params import JenkinsConfigParser

class Job(object):
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
        
        :param str url: Full URL of the Jenkins instance to connect to. Must be
            a valid running Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and 
            password for authenticating to the URL
            If omitted, credentials will be loaded from any pyjen config files found on the system
            If no credentials can be found, anonymous access will be used
        :returns: :py:mod:`pyjen.Jenkins` object, pre-configured with the 
            appropriate credentials and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.Jenkins`
        """
        # Default to anonymous access
        username = None
        password = None

        # If not explicit credentials provided, load credentials from any config files
        if not credentials:
            config = JenkinsConfigParser()
            config.read(JenkinsConfigParser.get_default_configfiles())
            credentials = config.get_credentials(url)
            
        # If explicit credentials have been found, use them rather than use anonymous access 
        if credentials:
            username = credentials[0]
            password = credentials[1]
        
        http_io = data_requester(url, username, password)
        retval = Job(http_io)
        
        # Sanity check: make sure we can successfully parse the view's name from the IO controller
        # to make sure we have a valid configuration
        try:
            name = retval.name
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Job. \
                Please check configuration.", http_io) 
        if name == None or name == "":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Job. \
                Please check configuration.", http_io) 
    
        return retval
        
    @property
    def name(self):
        """Returns the name of the job managed by this object
        
        :returns: The name of the job
        :rtype: :func:`str`
        """
        data = self.__data_io.get_api_data()      
        return data['name']
    
    @property
    def is_disabled(self):
        """Indicates whether this job is disabled or not
        
        :returns:
            true if the job is disabled, otherwise false
        :rtype: :func:`bool`
        """
        data = self.__data_io.get_api_data()
        
        return data['color'] == "disabled"
    
    @property
    def has_been_built(self):
        """Checks to see whether this job has ever been built or not
        
        :returns: True if the job has been built at least once, otherwise false
        :rtype: :py:module:`bool`
        """
        
        data = self.__data_io.get_api_data()
        
        return data['color'] != "notbuilt"
    
    @property
    def recent_builds(self):
        """Gets a list of the most recent builds for this job
        
        Rather than returning all data on all available builds, this
        method only returns the latest 20 or 30 builds. This list is
        synonymous with the short list provided on the main info
        page for the job on the dashboard.
        
        :rtype: :func:`list` of :py:mod:`pyjen.Build` objects
        """
        data = self.__data_io.get_api_data()
        
        builds = data['builds']
        
        retval = []
        for cur_build in builds:
            temp_data_io = self.__data_io.clone(cur_build['url'])
            temp_build = Build(temp_data_io)
            retval.append(temp_build)
        
        return retval
    
    @property
    def last_good_build(self):
        """Gets the most recent successful build of this job
        
        Synonymous with the "Last successful build" permalink on the jobs' main status page
        
        
        :returns:
            object that provides information and control for the
            last build which completed with a status of 'success'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        data = self.__data_io.get_api_data()
        
        lgb = data['lastSuccessfulBuild']
        
        if lgb == None:
            return None
        
        temp_data_io = self.__data_io.clone(lgb['url'])
        return Build(temp_data_io)
        
    @property
    def last_build(self):
        """Returns a reference to the most recent build of this job
        
        Synonymous with the "Last Build" permalink on the jobs' main status page
        
        :returns:
            object that provides information and control for the
            most recent build of this job.
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        data = self.__data_io.get_api_data()
        
        last_build = data['lastBuild']
        
        if last_build == None:
            return None
        
        temp_data_io = self.__data_io.clone(last_build['url'])
        return Build (temp_data_io)
    
    @property
    def last_failed_build(self):
        """Returns a reference to the most recent build of this job with a status of "failed"
        
        Synonymous with the "Last failed build" permalink on the jobs' main status page
        
        :returns:
            Most recent build with a status of 'failed'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        data = self.__data_io.get_api_data()
        
        bld = data['lastFailedBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return Build(temp_data_io)
        
    @property        
    def last_stable_build(self):
        """Returns a reference to the most recent build of this job with a status of "stable"
        
        Synonymous with the "Last stable build" permalink on the jobs' main status page
        
        
        :returns:
            Most recent build with a status of 'stable'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        data = self.__data_io.get_api_data()

        bld = data['lastCompletedBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return Build(temp_data_io)
    
    @property
    def last_unsuccessful_build(self):
        """Returns a reference to the most recent build of this job with a status of "unstable"
        
        Synonymous with the "Last unsuccessful build" permalink on the jobs' main status page
        
        :returns:
            Most recent build with a status of 'unstable'
            If there are no such builds in the build history, this method returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        data = self.__data_io.get_api_data()

        bld = data['lastUnsuccessfulBuild']
        
        if bld == None:
            return None
        
        temp_data_io = self.__data_io.clone(bld['url'])
        return Build(temp_data_io) 
    
    @property
    def config_xml(self):
        """Gets the raw XML configuration for the job
        
        Used in conjunction with the set_config_xml method,
        callers are free to manipulate the raw job configuration
        as desired.
        
        :returns:
            the full XML tree describing this jobs configuration
        :rtype: :func:`str`
        """
        return self.__data_io.get_text('/config.xml')
    
    @property
    def downstream_jobs(self):
        """Gets the list of jobs to be triggered after this job completes
        
        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :py:mod:`pyjen.Job` objects
        """
        data = self.__data_io.get_api_data()
        
        jobs = data['downstreamProjects']
        
        retval = []
        
        for j in jobs:
            temp_data_io = self.__data_io.clone(j['url'])
            temp_job = Job(temp_data_io)
            retval.append(temp_job)
        
        return retval
    
    @property
    def all_downstream_jobs(self):
        """Gets the list of all jobs that depend on this job, including all indirect descendants
        
        Includes jobs triggered by this job, and all jobs triggered by those
        jobs, recursively for all downstream dependencies
        
        :returns: A list of 0 or more jobs which depend on this one
        :rtype:  :class:`list` of :py:mod:`pyjen.Job` objects
        """
        temp = self.downstream_jobs
        retval = temp
        for j in temp:
            retval.extend(j.all_downstream_jobs)
        return retval
    
    @property
    def upstream_jobs(self):
        """Gets the list of upstream dependencies for this job
        
        :returns: A list of 0 or more jobs that this job depends on
        :rtype: :class:`list` of :py:mod:`pyjen.Job` objects
        """
        data = self.__data_io.get_api_data()
        
        jobs = data['upstreamProjects']
        
        retval = []
                
        for j in jobs:
            temp_data_io = self.__data_io.clone(j['url'])
            temp_job = Job(temp_data_io)
            retval.append(temp_job)
        
        return retval   
    
    @property
    def all_upstream_jobs(self):
        """Gets the list of all jobs that this job depends on, including all indirect descendants
        
        Includes jobs that trigger this job, and all jobs trigger those
        jobs, recursively for all upstream dependencies
        
        :returns: A list of 0 or more jobs this job depend on
        :rtype:  :class:`list` of :py:mod:`pyjen.Job` objects
        """
        temp = self.upstream_jobs
        retval = temp
        for j in temp:
            retval.extend(j.all_upstream_jobs)

        return retval
    
    @property
    def scm(self):
        """Gets the object that manages the source code management configuration for a job
        
        :returns:
            One of several possible plugin objects which exposes the relevant set
            of properties supported by a given source code management tool.
        :rtype: :py:class:`pyjen.plugins.pluginbase`    
        """
        xml = self.config_xml
        jobxml = job_xml(xml)
        return jobxml.get_scm()

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
        
    def delete (self):
        """Deletes this job from the Jenkins dashboard"""
        self.__data_io.post("/doDelete")    
        
    def get_build_by_number(self, build_number):
        """Gets a specific build of this job from the build history
        
        :param int build_number:
            Numeric identifier of the build to retrieve
            Value is typically non-negative
        :returns:
            Build object for the build with the given numeric identifier
            If such a build does not exist, returns None
        :rtype: :py:mod:`pyjen.Build`
        """
        temp_data_io = self.__data_io.clone(self.__data_io.url + "/" + str(build_number))

        # Lets try loading data from the given URL to see if it is valid. 
        # If it's not valid we'll assume a build with the given number doesn't exist 
        try:
            temp_data_io.get_api_data()
        except AssertionError:
            return None
        
        return Build(temp_data_io)
    
    def get_builds_in_time_range(self, start_time, end_time):
        """ Returns a list of all of the builds for a job that 
            occurred between the specified start and end times
            
            :param datetime start_time: 
                    starting time index for range of builds to find
            :param datetime end_time:
                    ending time index for range of builds to find
            :returns: a list of 0 or more builds
            :rtype: :class:`list` of :py:mod:`pyjen.Build` objects            
        """       
        if start_time > end_time:
            tmp = end_time
            end_time = start_time
            start_time = tmp
            
        builds = []                
        
        for run in self.recent_builds:            
            if run.build_time < start_time:
                break
            elif run.build_time >= start_time and run.build_time <= end_time:
                builds.append(run)                               
        return builds
        
    
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
        xml = self.config_xml
        
        jobxml = job_xml(xml)
        jobxml.set_custom_workspace(path)
        
        self.set_config_xml(jobxml.get_xml())
        
if __name__ == "__main__":
    pass
