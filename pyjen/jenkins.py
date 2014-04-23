import json
from pyjen.view import view
from pyjen.node import node
from pyjen.job import job
from pyjen.utils.data_requester import data_requester

class jenkins(object):
    """Python wrapper managing a Jenkins primary dashboard
    
    Generally you should use this class as the primary entry
    point to the PyJen APIs. Finer grained control of each
    aspect of the Jenkins dashboard is then provided by the
    objects exposed by this class including:
    
    * pyjen.job - abstraction for a Jenkins job, allowing manipulation
                    of job settings and controlling builds of those jobs
    * pyjen.build - abstraction for an instance of a build of a particular job
    * pyjen.view - abstraction for a view on the dashboard, allowing jobs to
                be filtered based on different criteria like job name.
    
    Example: finding a job
    ----------------------
    j = pyjen.jenkins('http://localhost:8080/', 'me', 'pwd')
    job= j.find_job('My Job')
    if job = None:
        print 'no job by that name found'
    else:
        print 'job ' + job.get_name() + ' found at ' + job.get_url()
        
        
        
    Example: finding the build number of the last good build 
            of the first job on the default view
    ----------------------------------------------------------
    j = pyjen.jenkins('http://localhost:8080/', 'me', 'pwd')
    view = j.get_default_view()
    jobs = view.get_jobs()
    lgb = jobs[0].get_last_good_build()
    print 'last good build of the first job in the default view is ' + lgb.get_build_number()
    """
    
    def __init__ (self, url, user=None, password=None):
        """constructor
        
        Parameter
        ---------
        url : string
            Full web URL to the main Jenkins dashboard
        user : string
            optional user name to use when authenticating to Jenkins
            if not defined unauthenticated access will be attempted
        password : string
            optional password for authenticating the given user
            if a non empty user name is given this parameter must be provided
            as well
        """
        if (user != None):
            assert (password != None)

        self.__url = url
        
        self.__requester = data_requester(self.__url, user, password)
        
    def get_url(self):
        """Gets the URL of the Jenkins dashboard associated with this object
        
        Return
        ------
        string
            URL associated with this object
        """

        return self.__url
    
    def get_views(self):
        """Gets a list of all views defined on the Jenkins dashboard
        
        Return
        ------
        list[pyjen.view]
            list of one or more views defined on this Jenkins instance.
        """
        data = self.__requester.get_data('/api/python')
        
        raw_views = data['views']
        retval = []
        
        for v in raw_views:
            if v['url'] == self.__url + "/":
                retval.append(view(v['url'] + "view/" + v['name']))
            else:
                retval.append(view(v['url']))
                        
        return retval
    
    def get_default_view(self):
        """returns a reference to the primary / default Jenkins view
        
        The default view is the one displayed when navigating to
        the main URL. Typically this will be the "All" view.
        
        Return
        ------
        pyjen.view
            object that manages the default Jenkins view
        """        
        data = self.__requester.get_data('/api/python')
        
        default_view = data['primaryView']
        return view(default_view['url'] + "view/" + default_view['name'])
    
    def get_nodes(self):
        """gets the list of nodes (aka: agents) managed by this Jenkins master
        
        Return
        ------
        list[pyjen.node]
            list of 0 or more node objects managed by this Jenkins master
        """
        data = self.__requester.get_data('/api/python')
                
        nodes = data['computer']
        retval = []
        for n in nodes:
            if n['displayName'] == 'master':
                retval.append(node(self.__url + '/computer/(master)'))
            else:
                retval.append(node(self.__url + '/computer/' + n['displayName']))
                        
        return retval
    
    def get_version(self):
        """Gets the version of Jenkins pointed to by this object
        
        Returns
        -------
        string
            Version number of the currently running Jenkins instance
        """
        headers = self.__requester.get_headers('/api/python')
        
        if not 'x-jenkins' in headers:
            return "Unknown"
        else:
            return headers['x-jenkins']
        
    def prepare_shutdown(self):
        """Sends a shutdown signal to the Jenkins master preventing new builds from executing
        
        Analogous to the "Prepare for Shutdown" link on the Manage Jenkins configuration page
        
        You can cancel a previous requested shutdown using the pyjen.jenkins.cancel_shutdown() method
        """
        self.__requester.post('/quietDown')
        
    def cancel_shutdown(self):
        """Cancels a previous scheduled shutdown sequence
        
        Cancels a shutdown operation initiated by the pyjen.jenkins.prepare_shutdown() method
        """
        self.__requester.post('/cancelQuietDown')
    
    def is_shutting_down(self):
        """checks to see whether the Jenkins master is in the process of shutting down.
        
        Return
        ------
        boolean
            If the Jenkins master is preparing to shutdown (ie: in quiet down state),
            return true, otherwise returns false.
        """
        data = self.__requester.get_data('/api/python')
        
        return data['quietingDown']
      
    def find_job(self, job_name):
        """Searches all jobs managed by this Jenkins instance for a specific job
        
        Parameter
        ---------
        job_name : string
            the name of the job to search for
            
        Return
        ------
        object : pyjen.job
            If a job with the specified name can be found, and object
            to manage the job will be returned, otherwise an empty
            object is returned (ie: None)
        """
        data = self.__requester.get_data('/api/python')
        tjobs = data['jobs']
    
        for tjob in tjobs:
            if tjob['name'] == job_name:
                return job(tjob['url'])
        
        return None
    
    def find_view(self, view_name):
        """Searches all views managed by this Jenkins instance for a specific view
        
        Parameter
        ---------
        view_name : string
            the name of the view to search for
            
        Return
        ------
        object : pyjen.view
            If a view with the specified name can be found, and object
            to manage the view will be returned, otherwise an empty
            object is returned (ie: None)
        """
        data = self.__requester.get_data('/api/python')
        
        raw_views = data['views']
        
        for v in raw_views:
            if v['name'] == view_name:
                return view(v['url'])
                        
        return None

    def create_view(self, view_name, view_type = view.LIST_VIEW):
        """Creates a new view on the Jenkins dashboard
        
        Parameters
        ----------
        view_name : string
            the name for this new view
            This name should be unique, different from any other views
            currently managed by the Jenkins instance
        view_type : string
            type of view to create
            must match one or more of the available view types supported
            by this Jenkins instance. See attributes of the pyjen.view
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

    j = jenkins("http://localhost:8080")
    v = j.get_default_view()
    print (v.get_name())