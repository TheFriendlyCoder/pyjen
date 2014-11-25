import xml.etree.ElementTree as ElementTree
from pyjen.utils.pluginapi import PluginBase


class ModuleLocation(object):
    def __init__(self, node):
        self._root = node

    @property
    def url(self):
        return self._root.find('remote').text

    def set_url(self, new_url):
        self._root.find('remote').text = new_url


    @property
    def local_dir(self):
        return self._root.find('local').text

    def set_local_dir(self, new_dir):

        self._root.find('local').text = new_dir

    @property
    def depth_option(self):
        return self._root.find('depthOption').text

    @property
    def ignore_externals(self):
        temp = self._root.find('ignoreExternalsOption').text
        assert temp.lower() == "true" or temp.lower() == "false"
        return temp.lower() == "true"

    def enable_ignore_externals(self):
        self._root.find('ignoreExternalsOption').text = "true"
    def disable_ignore_externals(self):
        self._root.find('ignoreExternalsOption').text = "false"

class Subversion(PluginBase):
    """Subversion SCM plugin"""
    
    def __init__(self, node):
        """constructor
        
        :param node: ElementTree node initialized with the XML from the Jenkins job
        """
        self._root = node
        assert (self._root.tag == "scm")
        assert (self._root.attrib['class'] == "hudson.scm.SubversionSCM")
        
    def get_locations(self):
        """Gets the list of SVN URLs associated with this plugin instance
        
        :returns:
            set of 0 or more ModuleLocation objects describing the SVN parameters for this module.
        :rtype: :class:`list` of :class:`ModuleLocation` objects
        """
        retval = []
        
        locations_node = self._root.find("locations")
        for loc in locations_node:
            retval.append(ModuleLocation(loc))
            
        return retval

    @property
    def included_regions(self):
        temp = self._root.find("includedRegions").text
        if temp is None:
            return []
        return temp.split()

    def set_included_regions(self, new_regions):
        self._root.find("includedRegions").text = "\n".join(new_regions)

    type = "hudson.scm.SubversionSCM"
