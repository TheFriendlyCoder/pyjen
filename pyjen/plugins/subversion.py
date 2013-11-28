#import xml.etree.ElementTree as ElementTree
from pyjen.plugins.pluginbase import pluginbase

class subversion(pluginbase):
    """Subversion SCM plugin"""
    
    def __init__(self, xml):
        """constructor
        
        Parameters
        ----------
        xml : string
            the XML text for the subtree of the SVN plugin
        """
        super(subversion, self).__init__(xml)
    
        assert (self._pluginbase__root.tag == "scm")
        assert (self._pluginbase__root.attrib['class'] == "hudson.scm.SubversionSCM")
        
    def get_modules(self):
        """Gets the list of SVN repositories (aka: modules) being used by the target job
        
        Returns
        -------
        list[string]
            set of 0 or more paths to SVN repositories being monitored
        """
        retval = []
        
        locations_node = self._pluginbase__root.find("locations")
        for loc in locations_node:
            val = {}
            tmp = loc.find('remote')
            assert (tmp != None)
            val['url'] = tmp.text
            
            tmp = loc.find('local')
            assert(tmp != None)
            val['local_directory'] = tmp.text
            
            tmp = loc.find('depthOption')
            assert(tmp != None)
            val['depth'] = tmp.text
            
            tmp = loc.find('ignoreExternalsOption')
            assert(tmp != None)
            val['ignore_externals'] = tmp.text
            
            retval.append(val)
            
        return retval
        
        
        
    