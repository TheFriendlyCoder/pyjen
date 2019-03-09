"""Primitives for controlling plain text view sub-sections on a sectioned view

This is a plugin supported by the SectionedView plugin"""
import xml.etree.ElementTree as ElementTree


class TextSection(object):
    """One of several 'section' types defined for a sectioned view

    Sections of this type contain simple descriptive text

    :param node: XML node defining the settings for a ListView section
    :type node: :class:`ElementTree.Element`
    """
    def __init__(self, node):
        self._root = node

    @property
    def node(self):
        """Gets the XML tree describing this section"""
        return self._root

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.sectioned_view.TextSection"

    @staticmethod
    def create(section_name):
        """Factory method for creating a new Git SCM code block

        :param str section_name:
            Text to appear at the top of the section
        :rtype: :class:`pyjen.plugins.sectionedview_textsection.TextSection`
        """
        default_xml = """<hudson.plugins.sectioned__view.TextSection>
    <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator"/>
    </jobNames>
    <jobFilters/>
    <width>FULL</width>
    <alignment>CENTER</alignment>
    <text/>
    <style>NONE</style>
</hudson.plugins.sectioned__view.TextSection>"""
        root_node = ElementTree.fromstring(default_xml)

        name_node = ElementTree.SubElement(root_node, "name")
        name_node.text = section_name

        return TextSection(root_node)

    @property
    def name(self):
        """Gets the title text of this section

        :rtype: :class:`str`
        """
        name_node = self._root.find("name")
        assert name_node is not None
        return name_node.text


PluginClass = TextSection


if __name__ == "__main__":  # pragma: no cover
    pass
