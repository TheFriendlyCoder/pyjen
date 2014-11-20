#import xml.etree.ElementTree as ElementTree
from pyjen.plugins.pluginbase import pluginbase

class Subversion(pluginbase):
    """Subversion SCM plugin"""
    
    def __init__(self, xml):
        """constructor
        
        :param str xml: the XML text for the subtree of the SVN plugin
        """
        super(Subversion, self).__init__(xml)
    
        assert (self._root.tag == "scm")
        assert (self._root.attrib['class'] == "hudson.scm.SubversionSCM")
        
    def get_modules(self):
        """Gets the list of SVN repositories (aka: modules) being used by the target job
        
        :returns:
            set of 0 or repository configuration options exposed by this job. Each element
            will contain the following keys:
            
            * 'url' - the URL of the repository tree monitored by this job
            * 'local_directory' - the local working path, typically under the jobs workspace folder
            * 'depth' - indicates the depth under which the SCM checkout operation should go
            * 'ignore_externals'- boolean indicating whether SVN externals are being monitored
                            by any SCM triggers associated with this job.
        :rtype: :class:`list` of :func:`dict` objects
        """
        retval = []
        
        locations_node = self._root.find("locations")
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

    type = "hudson.scm.SubversionSCM"
