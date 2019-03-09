"""Primitives for working on Jenkins views of type 'SectionedView'"""
import logging
import xml.etree.ElementTree as ElementTree
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML


class SectionedView(View):
    """Interface to Jenkins views of type "SectionedView"

     Views of this type support groupings of jobs into 'sections'
     which each have their own filters

     :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    :param parent:
        PyJen object that "owns" this view. Typically this is a reference to
        the :class:`pyjen.jenkins.Jenkins` object for the current Jenkins
        instance but in certain cases this may be a different object like
        a :class:`pyjen.plugins.nestedview.NestedView`.

        The parent object is expected to expose a method named `create_view`
        which can be used to clone instances of this view.
    """

    def __init__(self, api, parent):
        super(SectionedView, self).__init__(api, parent)
        self._log = logging.getLogger(__name__)

    @property
    def sections(self):
        """
        :returns: a list of sections contained within this view
        :rtype: :class:`list` of one of the 'SectionedView' section types
        """
        vxml = SectionedViewXML(self.config_xml)
        return vxml.sections

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "sectionedview"


class ListViewSection(object):
    """One of several 'section' types defined for a sectioned view

    Represents sections of type 'ListView'
    """

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


class TextSection(object):
    """One of several 'section' types defined for a sectioned view

    Sections of this type contain simple descriptive text"""
    def __init__(self, node):
        """
        :param node: XML node defining the settings for a ListView section
        :type node: :class:`ElementTree.Element`
        """
        self._node = node


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

        retval = []
        for node in nodes:
            plugin = create_xml_plugin(node)
            if plugin is not None:
                retval.append(plugin)
            else:
                self._log.warning("Sectioned view plugin %s not found",
                                  get_plugin_name(node))

        return retval


PluginClass = SectionedView


if __name__ == "__main__":  # pragma: no cover
    pass
