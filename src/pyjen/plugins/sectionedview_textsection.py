"""Primitives for controlling plain text view sub-sections on a sectioned view

This is a plugin supported by the SectionedView plugin"""
from xml.etree import ElementTree
from pyjen.utils.xml_plugin import XMLPlugin


class TextSection(XMLPlugin):
    """One of several 'section' types defined for a sectioned view

    Sections of this type contain simple descriptive text
    """
    @property
    def name(self):
        """str: the title text of this section"""
        name_node = self._root.find("name")
        assert name_node is not None
        return name_node.text

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.plugins.sectioned_view.TextSection"

    @classmethod
    def instantiate(cls, section_name):
        """Factory method for creating a new Git SCM code block

        Args:
            section_name (str):
                Text to appear at the top of the section

        Returns:
            TextSection:
                instance of this class
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

        return cls(root_node)


PluginClass = TextSection


if __name__ == "__main__":  # pragma: no cover
    pass
