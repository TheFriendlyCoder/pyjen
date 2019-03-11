"""Primitives for working on Jenkins views of type 'SectionedView'"""
import logging
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.plugin_api import find_plugin
from pyjen.exceptions import PluginNotSupportedError


class SectionedView(View):
    """Interface to Jenkins views of type "SectionedView"

     Views of this type support groupings of jobs into 'sections'
     which each have their own filters

     :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(SectionedView, self).__init__(api)
        self._log = logging.getLogger(__name__)

    @property
    def sections(self):
        """
        :returns: a list of sections contained within this view
        :rtype: :class:`list` of one of the 'SectionedView' section types
        """
        vxml = SectionedViewXML(self.config_xml)
        return vxml.sections

    def add_section(self, section_type, name):
        """Adds a new section to the sectioned view

        :param str section_type:
            name of class used to implement the new section to add
        :param str name:
            descriptive text to appear in the title area of the section
        """
        vxml = SectionedViewXML(self.config_xml)
        vxml.add_section(section_type, name)
        self.config_xml = vxml.xml

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.sectioned_view.SectionedView"


class SectionedViewXML(ViewXML):
    """raw config.xml parser for a Jenkins view of type 'Sectioned View'"""
    def __init__(self, xml):
        """
        :param str xml: XML string describing a sectioned view
        """
        super(SectionedViewXML, self).__init__(xml)
        self._log = logging.getLogger(__name__)

    @property
    def sections(self):
        """
        :returns: a list of all 'section' objects contained in this view
        :rtype: :class:`list` of section plugins associated with this view
        """
        nodes = self._root.find('sections')

        retval = list()
        for node in nodes:
            plugin = find_plugin(node.tag)
            if plugin is not None:
                retval.append(plugin(node))
            else:
                self._log.warning("Sectioned view plugin not found: %s",
                                  node.tag)

        return retval

    def add_section(self, section_type, name):
        """Adds a new section to the sectioned view

        :param str section_type:
            name of class used to implement the new section to add
        :param str name:
            descriptive text to appear in the title area of the section
        """
        plugin_class = find_plugin(section_type)
        if not plugin_class:
            raise PluginNotSupportedError(
                "Failed loading Sectioned View section",
                section_type)
        new_section = plugin_class.create(name)
        sections = self._root.find('sections')
        sections.append(new_section.node)


PluginClass = SectionedView


if __name__ == "__main__":  # pragma: no cover
    pass
