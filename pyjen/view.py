from pyjen.utils.data_requester import data_requester
from pyjen.job import job
from pyjen.utils.view_xml import view_xml
import re

class view(object):
    """Class that encapsulates all Jenkins related 'view' information
    
    Views are essentially just filters used to sort through jobs
    on the dashboard. Every job must be a member of one or more
    views.
    """
    
    #Class names for all supported view types
    LIST_VIEW = 'hudson.model.ListView'
    
    def __init__ (self, url, http_io_class=data_requester):
        """constructor
        
        :param str url:
            URL of the view to be managed. This may be a full URL, starting with
            the root Jenkins URL, or a partial URL relative to the Jenkins root
            
            Examples: 
                * 'http://jenkins/views/view1'
                * 'views/view1'
                
        :param obj http_io_class: 
            class capable of handling HTTP IO requests between
            this class and the Jenkins REST API
            If not explicitly defined a standard IO class will be used 
        """
        self.__requester = http_io_class(url)

        
    def get_url(self):
        """Returns the root URL for the REST API that manages this view
        
        :returns: the root URL for the REST API that controls this view
        :rtype: :func:`str`
        """

        return self.__requester.url
    
    def get_name(self):
        """Gets the display name for this view
        
        This is the name as it appears in the tabed view
        of the main Jenkins dashboard
        
        :returns: the name of the view
        :rtype: :func:`str`
        """
        data = self.__requester.get_api_data()
        return data['name']
        
    def get_jobs (self):
        """Gets a list of jobs associated with this view
        
        Views are simply filters to help organize jobs on the
        Jenkins dashboard. This method returns the set of jobs
        that meet the requirements of the filter associated
        with this view.
        
        :returns: list of 0 or more jobs that are included in this view
        :rtype:  :class:`list` of :py:mod:`pyjen.job` objects
        """
        data = self.__requester.get_api_data()
        
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
        :py:func:`pyjen.view.set_config_xml` method to dynamically
        update arbitrary properties of this view.
        
        :returns:
            returns the raw XML of the views configuration in
            a plain text string format
        :rtype: :func:`str`
        """
        return self.__requester.get_text("/config.xml")
        
    def set_config_xml(self, new_xml):
        """Updates the raw configuration of this view with a new set of properties
        
        This method should typically used in conjunction with
        the :py:func:`pyjen.view.get_config_xml` method.
        
        :param str new_xml:
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
        
        :returns: descriptive string of the Jenkins view type this view derives from
        :rtype: :func:`str`
        """
        xml = self.get_config_xml()
        vxml = view_xml(xml)
        return vxml.get_type() 
    
    def delete_all_jobs(self):
        """Helper method that allows callers to do bulk deletes of all jobs found in this view"""
        
        my_jobs = self.get_jobs()
        for j in my_jobs:
            j.delete()
            
    def disable_all_jobs(self):
        """Helper method that allows caller to bulk-disable all jobs found in this view""" 
        my_jobs = self.get_jobs()
        for j in my_jobs:
            print ("disabling " + j.get_name())
            j.disable()
            
    def enable_all_jobs(self):
        """Helper method that allows caller to bulk-enable all jobs found in this view"""
        my_jobs = self.get_jobs()
        for j in my_jobs:
            j.enable()
            
    def clone_all_jobs(self, search_regex, replacement_string):
        """Helper method that does a batch clone on all jobs found in this view
        
        :param str search_regex: pattern to match against all jobs
            contained in this view, to be modified in order to generate
            new job names for their cloned counterparts.
        :param str replacement_string: character string to substitute in place
            of the regex pattern when generating names for the new
            cloned jobs.
        :returns: list of newly created jobs
        :rtype: :class:`list` of :py:mod:`pyjen.job` objects
        """
        my_jobs = self.get_jobs()
        retval = []
        for j in my_jobs:
            orig_name = j.get_name()
            new_name = re.sub(search_regex, replacement_string, orig_name)
            new_job = j.clone(new_name)
            retval.append(new_job)
        return retval
    
if __name__ == "__main__":
    pass