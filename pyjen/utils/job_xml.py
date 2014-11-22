import xml.etree.ElementTree as ElementTree
from pyjen.utils.pluginapi import get_plugins
from pyjen.plugins.pluginbase import pluginbase
from pyjen.exceptions import PluginNotSupportedError

class job_xml(object):
    """ Wrapper around the config.xml for a Jenkins job
    
    The source xml can be loaded from nearly any URL by
    appending "/config.xml" to it, as in "http://server/jobs/job1/config.xml"
     
    """
    def __init__ (self, xml):
        """Constructor
        
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        
        self.__root = ElementTree.fromstring(xml)

        assert (self.__root.tag == "project")

    def set_custom_workspace(self, path):
        """Defines a new or modified custom workspace for a job
        
        If the job already has a custom workspace it will be replaced with the given path
        If not then a new custom workspace will be created with the given path
        
        :param str path: path of the new or modified custom workspace
        """
        Node = self.__root.find('customWorkspace')
        
        if Node == None:
            Node = ElementTree.SubElement(self.__root, 'customWorkspace')

        Node.text = path

    def disable_custom_workspace(self):
        """Disables a jobs use of a custom workspace
        
        If the job is not currently using a custom workspace this method will do nothing
        """
    
        Node =  self.__root.find('customWorkspace')
        
        if Node != None:
            self.__root.remove(Node)
                        
    def get_xml(self):
        """Extracts the processed XML for export to a Jenkins job
        
        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.
        
        :rtype: :func:`str`
        """
        retval = ElementTree.tostring(self.__root, "UTF-8")
        return retval.decode("utf-8")
    
    def get_scm(self):
        """Retrieves the appropriate plugin for the SCM portion of a job
        
        Detects which source code management tool is being used by this
        job, locates the appropriate plugin for that tool, and returns
        an instance of the wrapper for that plugin pre-configured with
        the settings found in the relevant XML subtree.
        
        :returns: 
            One of any number of plugin objects responsible for providing
            extensions to the source code management portion of a job
        
            Examples: :py:mod:`pyjen.plugins.Subversion`
        
        :rtype: :py:mod:`pyjen.plugins.pluginbase`
        """
        Node = self.__root.find('scm')
        xml = ElementTree.tostring(Node)

        pluginxml = pluginbase(xml)
        for plugin in get_plugins():
            if plugin.type == pluginxml.get_class_name():
                return plugin(xml)

        raise PluginNotSupportedError("Job XML plugin {0} not found".format(pluginxml.get_class_name()), pluginxml.get_class_name())

