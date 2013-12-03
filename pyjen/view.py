from utils.data_requester import data_requester
from job import job
from utils.view_xml import view_xml

class view(object):
    """Class that encapsulates all Jenkins related 'view' information
    
    Views are essentially just filters used to sort through jobs
    on the dashboard. Every job must be a member of one or more
    views.
    """
    
    #Class names for all supported view types
    LIST_VIEW = 'hudson.model.ListView'
    
    def __init__ (self, url, user=None, password=None):
        """constructor
        
        Parameters
        ----------
        url : string
            root URL of the view being managed by this object
            Example: 'http://jenkins/view/MyView/'
        user : string
            optional user name to authenticate with Jenkins
        password : string
            optional password for the specified user
            if a user name is provided this parameter must be non-empty
        """
        if (user != None):
            assert (password != None)
        
        self.__url = url
        self.__requester = data_requester(self.__url, user, password)

        
    def get_url(self):
        """Returns the root URL for the REST API that manages this view
        
        Return
        ------
        string
            the root URL for the REST API that controls this view
        """

        return self.__url
    
    def get_name(self):
        """Gets the display name for this view
        
        This is the name as it appears in the tabed view
        of the main Jenkins dashboard
        
        Return
        ------
        string
            the name of the view
        """
        data = self.__requester.get_data("/api/python")
        
        return data['name']
        
    def get_jobs (self):
        """Gets a list of jobs associated with this view
        
        Views are simply filters to help organize jobs on the
        Jenkins dashboard. This method returns the set of jobs
        that meet the requirements of the filter associated
        with this view.
        
        Return
        ------
        list[pyjen.job]
            list of 0 or more jobs that are included in this view
        """
        data = self.__requester.get_data("/api/python")
        
        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:        
            retval.append(job(j['url']))
            
        return retval
    
    def get_config_xml(self):
        """Gets the raw configuration data in XML format
        
        This is an advanced function which allows the caller
        to manually manipulate the raw configuration settings
        of the view. Use with caution.
        
        This method can be used in conjunction with the 
        pyjen.view.set_config_xml() method to dynamically
        update arbitrary properties of this view.
        
        Return
        ------
        string
            returns the raw XML of the views configuration in
            a plain text string format
        """
        return self.__requester.get_text("/config.xml")
        
    def set_config_xml(self, new_xml):
        """Updates the raw configuration of this view with a new set of properties
        
        This method should typically used in conjunction with
        the pyjen.view.get_config_xml() method.
        
        Parameter
        ---------
        new_xml : string
            XML encoded text string to be used as a replacement for the
            current configuration being used by this view.
            
            NOTE: It is assumed that this input text meets the schema
            requirements for a Jenkins view.
        """
        #TODO: Find a link to the schema for views and put it here
        #      in the comments
        headers = {'Content-Type': 'text/xml'}
        args = {}
        args['data'] = new_xml
        args['headers'] = headers
        
        self.__requester.post("/config.xml", **args)
        
    def delete(self):
        """Deletes this view from the dashboard"""
        self.__requester.post("/doDelete")
        
    def get_type(self):
        """Gets the Jenkins view-type descriptor for this view
        
        Returns
        -------
        string
            descriptive string of the Jenkins view type this view derives from
        """
        
        xml = self.get_config_xml()
        vxml = view_xml(xml)
        return vxml.get_type() 
        
        
        
if __name__ == "__main__":
    v = view("http://builds/view/unified")
    print v.get_type()