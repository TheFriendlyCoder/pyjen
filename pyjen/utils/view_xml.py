import xml.etree.ElementTree as ElementTree

class view_xml(object):
    def __init__ (self, xml):
        """Constructor
        
        :param str xml: Raw XML character string extracted from a Jenkins job.
        """
        
        self.__root = ElementTree.fromstring(xml)

    def get_type(self):
        """Returns the Jenkins type descriptor for this view
        
        :returns: type descriptor of this view
        :rtype: :func:`str`
        """
        
        #The root element of the views configuration XML
        #defines the kind of view. Specifically we need
        #to examine the tag of the root element to get
        #the appropriate class name 
        retval = self.__root.tag
        
        #For some reason single underscores in the view type
        #are replaced by double underscores in the element tag name
        #so we reverse that here
        retval = retval.replace("__", "_")
        
        #TODO: Add support for this via the plugin API
        #TODO: Confirm built in types never have this problem
        #TODO: Confirm that all view plugins give a plugin attribute on this node
        
        return retval
        