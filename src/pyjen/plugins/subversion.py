"""Module defining the interfaces for interacting with Subversion properties
associated with a :py:mod:`pyjen.job.Job`"""
from pyjen.utils.xml_plugin import XMLPlugin


class Subversion(XMLPlugin):
    """Subversion SCM job plugin

    https://wiki.jenkins-ci.org/display/JENKINS/Subversion+Plugin
    """
    @property
    def locations(self):
        """list (ModuleLocation): set of 0 or more ModuleLocation objects
        describing the SVN parameters for this module."""
        retval = []

        locations_node = self._root.find("locations")
        for loc in locations_node:
            retval.append(ModuleLocation(loc))

        return retval

    @property
    def included_regions(self):
        """list (str): patterns of the regions of the SVN repo to include in
        SCM operations"""
        temp = self._root.find("includedRegions").text
        if temp is None:
            return []
        return temp.split()

    @included_regions.setter
    def included_regions(self, new_regions):
        self._root.find("includedRegions").text = "\n".join(new_regions)

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "subversion"


class ModuleLocation(XMLPlugin):
    """Interface to SCM module declarations in a Subversion property of a job"""

    @property
    def node(self):
        """xml.etree.ElementTree.Element: the XML node associated with this
        plugin"""
        return self._root

    @property
    def url(self):
        """str: SVN URL where the source code for this module can be found"""
        return self._root.find('remote').text

    @url.setter
    def url(self, new_url):
        self._root.find('remote').text = new_url

    @property
    def local_dir(self):
        """str: folder where the source code for this module is checked out to
        """
        return self._root.find('local').text

    @local_dir.setter
    def local_dir(self, new_dir):
        self._root.find('local').text = new_dir

    @property
    def depth_option(self):
        """str: the current SVN 'depth' options associated with this module"""
        return self._root.find('depthOption').text

    @property
    def ignore_externals(self):
        """bool: True if ignore externals is enabled, otherwise False"""
        temp = self._root.find('ignoreExternalsOption').text
        assert temp.lower() == "true" or temp.lower() == "false"
        return temp.lower() == "true"

    def enable_ignore_externals(self):
        """Enables the 'ignore externals' option on this SCM module"""
        self._root.find('ignoreExternalsOption').text = "true"

    def disable_ignore_externals(self):
        """Disables the 'ignore externals' option on this SCM module"""
        self._root.find('ignoreExternalsOption').text = "false"


PluginClass = Subversion

if __name__ == "__main__":  # pragma: no cover
    pass
