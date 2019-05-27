"""Primitives for controlling list view sub-sections on a sectioned view

This is a plugin supported by the SectionedView plugin"""
import xml.etree.ElementTree as ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class ListViewSection(XMLPlugin):
    """One of several 'section' types defined for a sectioned view

    Represents sections of type 'ListView'
    """
    @property
    def name(self):
        """Gets the title text of this section

        :rtype: :class:`str`
        """
        name_node = self._root.find("name")
        assert name_node is not None
        return name_node.text

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
        self.update()

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.sectioned_view.ListViewSection"

    @classmethod
    def instantiate(cls, section_name):
        """Factory method for creating a new Git SCM code block

        :param str section_name:
            Text to appear at the top of the section
        :rtype: :class:`pyjen.plugins.sectionedview_listsection.ListViewSection`
        """
        default_xml = """<hudson.plugins.sectioned__view.ListViewSection>
    <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator"/>
    </jobNames>
    <jobFilters/>
    <width>FULL</width>
    <alignment>CENTER</alignment>
    <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastFailureColumn/>
        <hudson.views.LastDurationColumn/>
        <hudson.views.BuildButtonColumn/>
    </columns>
</hudson.plugins.sectioned__view.ListViewSection>"""
        root_node = ElementTree.fromstring(default_xml)

        name_node = ElementTree.SubElement(root_node, "name")
        name_node.text = section_name

        return cls(root_node)


PluginClass = ListViewSection


if __name__ == "__main__":  # pragma: no cover
    pass
