"""Primitives for working on Jenkins views of type 'SectionedView'"""
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.pluginapi import create_xml_plugin, PluginBase, get_plugin_name
import xml.etree.ElementTree as ElementTree
import logging

log = logging.getLogger(__name__)  # pylint: disable=C0103


class SectionedView(View):
    """Interface to Jenkins views of type "SectionedView"

     Views of this type support groupings of jobs into 'sections'
     which each have their own filters"""
    type = "hudson.plugins.sectioned__view.SectionedView"

    def __init__(self, controller, jenkins_master):
        """
        :param controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master:
            Reference to Jenkins object associated with the master instance managing
            this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`        """
        super(SectionedView, self).__init__(controller, jenkins_master)

    @property
    def sections(self):
        """
        :returns: a list of sections contained within this view
        :rtype: :class:`list` of one of the 'SectionedView' section types
        """
        vxml = SectionedViewXML(self.config_xml)
        return vxml.sections


class ListViewSection(PluginBase):
    """One of several 'section' types defined for a sectioned view

    Represents sections of type 'ListView'"""
    type = "hudson.plugins.sectioned__view.ListViewSection"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a ListView section
        :type node: :class:`ElementTree.Element`
        """
        self._root = node

    @property
    def include_regex(self):
        """regular filter for jobs to be shown in this section

        :rtype: :class:`str`
        """
        regex_node = self._root.find("includeRegex")
        if regex_node is None:
            return ""
        return regex_node.text

    @include_regex.setter
    def include_regex(self, new_regex):
        """Sets the filter to use for jobs shown in this section

        :param str new_regex: a new regular expression to use for the filter
        """
        regex_node = self._root.find("includeRegex")
        if regex_node is None:
            regex_node = ElementTree.SubElement(self._root, 'includeRegex')
        regex_node.text = new_regex


class TextSection(PluginBase):
    """One of several 'section' types defined for a sectioned view

    Sections of this type contain simple descriptive text"""
    type = "hudson.plugins.sectioned__view.TextSection"

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a ListView section
        :type node: :class:`ElementTree.Element`
        """
        self._node = node


class SectionedViewXML(ViewXML):
    """Abstraction for operating on raw config.xml data for a Jenkins view of type 'Sectioned View'"""
    def __init__(self, xml):
        """
        :param str xml: XML string describing a sectioned view
        """
        super(SectionedViewXML, self).__init__(xml)

    @property
    def sections(self):
        """
        :returns: a list of all 'section' objects contained in this view
        :rtype: :class:`list` of section plugins associated with this view
        """
        nodes = self._root.find('sections')

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                log.warning("Sectioned view plugin {0} not found".format(get_plugin_name(node)))

        return retval


if __name__ == "__main__":  # pragma: no cover
    pass



