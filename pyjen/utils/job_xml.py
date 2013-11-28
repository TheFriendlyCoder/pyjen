import xml.etree.ElementTree as ElementTree
import pyjen.utils.pluginapi as pluginapi

class job_xml(object):
    """ Wrapper around the config.xml for a Jenkins job
    
    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
     
    """
    def __init__ (self, xml):
        """Constructor
        
        Parameters
        ----------
        xml : string
            Raw XML character string extracted from a Jenkins job.
        """
        
        self.__root = ElementTree.fromstring(xml)

        assert (self.__root.tag == "project")

    def set_custom_workspace(self, path):
        """Defines a new or modified custom workspace for a job
        
        If the job already has a custom workspace it will be replaced with the given path
        If not then a new custom workspace will be created with the given path
        
        Parameters
        ----------
        path : string
            path of the new or modified custom workspace
        """
        node = self.__root.find('customWorkspace')
        
        if node == None:
            node = ElementTree.SubElement(self.__root, 'customWorkspace')

        node.text = path

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace
        
        If the job is not currently using a custom workspace this method will do nothing
        """
    
        node =  self.__root.find('customWorkspace')
        
        if node != None:
            self.__root.remove(node)
                        
    def get_xml(self):
        """Extracts the processed XML for export to a Jenkins job
        
        Returns
        -------
        string
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.
        """
        
        #TODO: handle the unicode encoding here correctly
        return ElementTree.tostring(self.__root, "UTF-8")
    
    def get_scm(self):
        """Retrieves the appropriate plugin for the SCM portion of a job
        
        Detects which source code management tool is being used by this
        job, locates the appropriate plugin for that tool, and returns
        an instance of the wrapper for that plugin pre-configured with
        the settings found in the relevant XML subtree.
        
        Return
        ------
        object
            One of any number of plugin objects responsible for providing
            extensions to the source code management portion of a job
            
            Examples: pyjen.pluings.subversion
        """
        node = self.__root.find('scm')
        xml = ElementTree.tostring(node)
        
        return pluginapi.find_plugin(xml)

    