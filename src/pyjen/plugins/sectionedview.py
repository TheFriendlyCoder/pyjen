"""Primitives for working on Jenkins views of type 'SectionedView'"""
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.plugin_api import find_plugin


class SectionedView(View):
    """Interface to Jenkins views of type "SectionedView"

    Views of this type support groupings of jobs into 'sections'
    which each have their own filters
    """
    # ----------------------------------------------------- XML BASED PROPERTIES
    @property
    def sections(self):
        """
        :returns: a list of sections contained within this view
        :rtype: :class:`list` of one of the 'SectionedView' section types
        """
        return self._view_xml.sections

    def add_section(self, section_type, name):
        """Adds a new section to the sectioned view

        :param str section_type:
            name of class used to implement the new section to add
        :param str name:
            descriptive text to appear in the title area of the section
        """
        self._view_xml.add_section(section_type, name)
        self._view_xml.update()

    # --------------------------------------------------------------- PLUGIN API
    @property
    def _xml_class(self):
        return SectionedViewXML

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

    @property
    def sections(self):
        """
        :returns: a list of all 'section' objects contained in this view
        :rtype: :class:`list` of section plugins associated with this view
        """
        nodes = self._root.find('sections')

        retval = list()
        for node in nodes:
            plugin_class = find_plugin(node.tag)
            if plugin_class is None:
                self._log.warning("Sectioned view plugin not found: %s",
                                  node.tag)
                continue
            temp = plugin_class(node)
            temp.parent = self
            retval.append(temp)

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
            raise NotImplementedError(
                "Failed loading Sectioned View section: " +
                section_type)
        new_section = plugin_class.instantiate(name)
        new_section.parent = self
        sections = self._root.find('sections')
        sections.append(new_section.node)


PluginClass = SectionedView


if __name__ == "__main__":  # pragma: no cover
    pass
