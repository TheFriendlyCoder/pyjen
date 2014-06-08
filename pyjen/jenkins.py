import json
from pyjen.view import view
from pyjen.node import node
from pyjen.job import job
from pyjen.utils.data_requester import data_requester
from pyjen.user_params import GlobalParams
from pyjen.exceptions import InvalidJenkinsURLError

class jenkins(object):
    """Python wrapper managing a Jenkins primary dashboard
    
    Generally you should use this class as the primary entry
    point to the PyJen APIs. Finer grained control of each
    aspect of the Jenkins dashboard is then provided by the
    objects exposed by this class including:
    
    * :py:mod:`pyjen.job` - abstraction for a Jenkins job, allowing manipulation
                    of job settings and controlling builds of those jobs
    * :py:mod:`pyjen.build` - abstraction for an instance of a build of a particular job
    * :py:mod:`pyjen.view` - abstraction for a view on the dashboard, allowing jobs to
                be filtered based on different criteria like job name.
    
    **Example:** finding a job ::
    
        j = pyjen.jenkins('http://localhost:8080')
        job= j.find_job('My Job')
        if job = None:
            print ('no job by that name found')
        else:
            print ('job ' + job.get_name() + ' found at ' + job.get_url())
        
        
    **Example:** finding the build number of the last good build of the first job on the default view ::
    
        j = pyjen.jenkins('http://localhost:8080/')
        view = j.get_default_view()
        jobs = view.get_jobs()
        lgb = jobs[0].get_last_good_build()
        print ('last good build of the first job in the default view is ' + lgb.get_build_number())
    
    """
    
    def __init__ (self, data_io_controller):
        """constructor
        
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
        
        :param str url: Full URL of the Jenkins instance to connect to. Must be a valid running Jenkins instance.
        :param tuple credentials: A 2-element tuple with the username and password for authenticating to the URL
            If no credentials can be found elsewhere, anonymous access will be chosen
        :returns: :py:mod:`pyjen.jenkins` object, pre-configured with the appropriate credentials
            and connection parameters for the given URL.
        :rtype: :py:mod:`pyjen.jenkins`
        """
        if credentials != None:
            username = credentials[0]
            password = credentials[1]
        else:
            username = ""
            password = ""
        
        http_io = data_requester(url, username, password)
        retval = jenkins(http_io)
        
        # Sanity check: make sure the given IO object can successfully query the Jenkins version number
        try:
            version = retval.get_version() 
        except:
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Jenkins. Please check configuration.", http_io)

        if version == None or version == "" or version == "Unknown":
            raise InvalidJenkinsURLError("Invalid connection parameters provided to PyJen.Jenkins. Please check configuration.", http_io)
        return retval
    
    def get_views(self):
        """Gets a list of all views defined on the Jenkins dashboard
        
        :returns: list of one or more views defined on this Jenkins instance. 
        :rtype: :func:`list` of :py:mod:`pyjen.view` objects
            
        """
        data = self.__data_io.get_api_data()
        
        raw_views = data['views']
        retval = []

        for v in raw_views:
            # The default view will not have a valid view URL
            # so we need to look for this and generate a corrected one
            turl = v['url']
            if turl.find('view') == -1:
                turl += "view/" + v['name']
                
            new_io_obj = self.__data_io.clone(turl)
            tview = view(new_io_obj)
            retval.append(tview)
            
        return retval
    
    def get_default_view(self):
        """returns a reference to the primary / default Jenkins view
        
        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view.
        
        :returns: object that manages the default Jenkins view
        :rtype: :py:mod:`pyjen.view`            
        """        
        data = self.__data_io.get_api_data()

        default_view = data['primaryView']
        new_io_obj = self.__data_io.clone(default_view['url'] + "view/" + default_view['name'])
        return view(new_io_obj)
    
    def get_nodes(self):
        """gets the list of nodes (aka: agents) managed by this Jenkins master
        
        :returns: list of 0 or more node objects managed by this Jenkins master 
        :rtype: :func:`list` of :py:mod:`pyjen.node` objects
            
        """
        data = self.__requester.get_api_data()
                
        nodes = data['computer']
        retval = []
        for n in nodes:
            if n['displayName'] == 'master':
                retval.append(node(self.get_url() + '/computer/(master)'))
            else:
                retval.append(node(self.get_url() + '/computer/' + n['displayName']))
                        
        return retval
    
    def get_version(self):
        """Gets the version of Jenkins pointed to by this object
        
        :return: Version number of the currently running Jenkins instance
        :rtype: :func:`str`
            
        """
        headers = self.__data_io.get_headers('/api/python')
        
        if not 'x-jenkins' in headers:
            return "Unknown"
        else:
            return headers['x-jenkins']
        
    def prepare_shutdown(self):
        """Sends a shutdown signal to the Jenkins master preventing new builds from executing
        
        Analogous to the "Prepare for Shutdown" link on the Manage Jenkins configuration page
        
        You can cancel a previous requested shutdown using the :py:meth:`pyjen.jenkins.cancel_shutdown` method
        """
        self.__data_io.post('/quietDown')
        
    def cancel_shutdown(self):
        """Cancels a previous scheduled shutdown sequence
        
        Cancels a shutdown operation initiated by the :py:meth:`pyjen.jenkins.prepare_shutdown` method
        """
        self.__data_io.post('/cancelQuietDown')
    
    def is_shutting_down(self):
        """checks to see whether the Jenkins master is in the process of shutting down.
        
        :returns: If the Jenkins master is preparing to shutdown (ie: in quiet down state),
            return true, otherwise returns false.
        :rtype: :func:`bool`
            
        """
        data = self.__data_io.get_api_data()
        
        return data['quietingDown']
      
    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job
        
        :param str job_name: the name of the job to search for
        :returns: If a job with the specified name can be found, and object
            to manage the job will be returned, otherwise an empty
            object is returned (ie: None)
        :rtype: :py:mod:`pyjen.job`
        """
        data = self.__data_io.get_api_data()
        tjobs = data['jobs']
    
        for tjob in tjobs:
            if tjob['name'] == job_name:
                return job(tjob['url'])
        
        return None
    
    def find_view(self, view_name):
        """Searches all views managed by this Jenkins instance for a specific view
        
        :param str view_name: the name of the view to search for
            
        :returns: If a view with the specified name can be found, an object
            to manage the view will be returned, otherwise an empty
            object is returned (ie: None)
        :rtype: :py:mod:`pyjen.view`
        """
        data = self.__data_io.get_api_data()
        
        raw_views = data['views']
        
        for v in raw_views:
            if v['name'] == view_name:
                turl = v['url']
                if turl.find('view') == -1:
                    turl += "view/" + v['name']
                
                new_io_obj = self.__data_io.clone(turl)
                return view(new_io_obj)
                        
        return None

    def create_view(self, view_name, view_type = view.LIST_VIEW):
        """Creates a new view on the Jenkins dashboard
        
        :param str view_name: the name for this new view
            This name should be unique, different from any other views
            currently managed by the Jenkins instance
        :param str view_type: type of view to create
            must match one or more of the available view types supported
            by this Jenkins instance. See attributes of the :py:mod:`pyjen.view`
            class for compatible options.
            Defaults to a list view type
        """
        #TODO: consider rethinking this method. Perhaps it'd be better
        #      suited to the view class. Alternatively, maybe we just
        #      construct the view class externally then insert it
        #      onto the dashboard here .... not sure.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }
        
        args = {}
        args['data'] = data
        args['headers'] = headers

        self.__requester.post('/createView', args)        
        
if __name__ == '__main__':
    j = jenkins.easy_connect("http://builds", ("builder", "CodeRocks!"))
    vs = j.get_views()
    for v in vs:
        print (v.get_name())