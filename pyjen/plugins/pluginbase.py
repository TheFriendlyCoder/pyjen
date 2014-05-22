import xml.etree.ElementTree as ElementTree

class pluginbase(object):
    """common base class for all PyJen plugins
    
    PyJen plugins are wrappers around native Jenkins plugins. Each
    Jenkins plugin inserts one or more XML elements into the configuration
    file for a job, with specific elements and attributes for each plugin.
    However, there are a few common properties exposed by all plugins
    which are exposed by this base class.
    """
    
    #Root element of the XML tree for this plugin
    #TIP: This member is accessible from derived classes using the following syntax:
    #           self._pluginbase__root
    __root = None
    
    def __init__(self, xml):
        """constructor
        
        :param str xml: the XML sub-tree defining the properties of this plugin
        """
        self.__root = ElementTree.fromstring(xml)
        
    def get_name(self):
        """Gets the name of the plugin
        
        :returns: the plugin name
        :rtype: :func:`str`
        """
        attr = self.__root.attrib['plugin']
        parts = attr.split('@')
        return parts[0]
        
    def get_classname(self):
        """Gets the Java class name of the plugin
        
        :returns: the Java class name
        :rtype: :func:`str`
        """
        return self.__root.attrib['classname']
        
    def get_version(self):
        """Gets the version of the plugin
        
        :returns: the plugin version
        :rtype: :func:`str`
        """
        attr = self.__root.attrib['plugin']
        parts = attr.split('@')
        return parts[1]