import xml.etree.ElementTree as ElementTree

class pluginbase(object):
    """common base class for all PyJen plugins
    
    PyJen plugins are wrappers around native Jenkins plugins. Each
    Jenkins plugin inserts one or more XML elements into the configuration
    file for a job, with specific elements and attributes for each plugin.
    However, there are a few common properties exposed by all plugins
    which are exposed by this base class.
    """
    def __init__(self, xml):
        """constructor
        
        :param str xml: the XML sub-tree defining the properties of this plugin
        """
        self._root = ElementTree.fromstring(xml)
        
    def get_module_name(self):
        """Gets the name of the plugin
        
        :returns: the plugin name
        :rtype: :func:`str`
        """
        attr = self._root.attrib['plugin']
        parts = attr.split('@')
        return parts[0]
        
    def get_class_name(self):
        """Gets the Java class name of the plugin
        
        :returns: the Java class name
        :rtype: :func:`str`
        """

        if self._root.has_attrib('classname'):
            temp = self._root.attrib['classname']
        else:
            temp = self._root.tag

        return temp.split(".")[-1]

        
    def get_version(self):
        """Gets the version of the plugin
        
        :returns: the plugin version
        :rtype: :func:`str`
        """
        attr = self._root.attrib['plugin']
        parts = attr.split('@')
        return parts[1]



if __name__ == "__main__": # pragma: no cover
    pass
