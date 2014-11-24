from pyjen.view import View
from pyjen.utils.view_xml import view_xml
import xml.etree.ElementTree as ElementTree


class sectioned_view(View):
    """Sectioned view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(sectioned_view, self).__init__(controller, jenkins_master)

    type = "hudson.plugins.sectioned_view.SectionedView"

class SectionedViewXMLPlugin(object):
    def __init__(self, node):
        self._root = node

    @staticmethod
    def create(node):
        temp_class = SectionedViewXMLPlugin._get_section_class(node.tag)

        import sys

        #print(sys.modules.keys())
        return temp_class(node)

    @staticmethod
    def _get_section_class(tagname):
        temp = tagname.split(".")
        #print(temp[-1])
        import importlib
        m = importlib.import_module("sectioned-view")
        c = getattr(m, temp[-1])
        #print(c)
        return c

    def get_xml(self):
        """Extracts the processed XML for export to a Jenkins job

        :returns:
            Raw XML containing any and all customizations applied in
            previous operations against this object. This character
            string can be imported into Jenkins to configure a job.

        :rtype: :func:`str`
        """
        retval = ElementTree.tostring(self._root, "UTF-8")
        return retval.decode("utf-8")

class ListViewSection(SectionedViewXMLPlugin):
    def __init__(self, node):
        super(ListViewSection, self).__init__(node)

    @property
    def includeRegex(self):
        regex_node = self._root.find("includeRegex")
        return regex_node.text

    def set_include_regex(self, new_regex):
        regex_node = self._root.find("includeRegex")
        regex_node.text = new_regex

    @property
    def type(self):
        return "ListViewSection"


class TextSection(SectionedViewXMLPlugin):
    def __init__(self, node):
        super(TextSection, self).__init__(node)

    @property
    def type(self):
        return "TextSection"

class SectionedViewXML(view_xml):
    def __init__(self, xml):
        """Constructor"""
        super(SectionedViewXML, self).__init__(xml)

    @property
    def sections(self):
        """Gets a list of all 'section' objects contained in this view"""
        sections_node = self._root.find('sections')
        retval = []
        for node in sections_node:
            retval.append(SectionedViewXMLPlugin.create(node))
        return retval


if __name__ == "__main__":
    sample = """<?xml version="1.0" encoding="UTF-8"?>
<hudson.plugins.sectioned__view.SectionedView plugin="sectioned-view@1.18">
  <name>trunk</name>
  <filterExecutors>true</filterExecutors>
  <filterQueue>true</filterQueue>
  <properties class="hudson.model.View$PropertyList"/>
  <sections>
    <hudson.plugins.sectioned__view.TextSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator"/>
      </jobNames>
      <jobFilters/>
      <name>Builds</name>
      <width>FULL</width>
      <alignment>CENTER</alignment>
      <text></text>
      <style>NONE</style>
    </hudson.plugins.sectioned__view.TextSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>32 Bit</name>
      <includeRegex>unified-trunk-.*-build-32</includeRegex>
      <width>HALF</width>
      <alignment>LEFT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>64 Bit</name>
      <includeRegex>unified-trunk-.*-build-64</includeRegex>
      <width>HALF</width>
      <alignment>RIGHT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.TextSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>Tests</name>
      <width>FULL</width>
      <alignment>CENTER</alignment>
      <text></text>
      <style>NONE</style>
    </hudson.plugins.sectioned__view.TextSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>32 Bit</name>
      <includeRegex>unified-trunk-.*-test-32</includeRegex>
      <width>HALF</width>
      <alignment>LEFT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>64 Bit</name>
      <includeRegex>unified-trunk-.*-test-64</includeRegex>
      <width>HALF</width>
      <alignment>RIGHT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.TextSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>Packages</name>
      <width>FULL</width>
      <alignment>CENTER</alignment>
      <text></text>
      <style>NONE</style>
    </hudson.plugins.sectioned__view.TextSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>32 Bit</name>
      <includeRegex>unified-trunk-.*-package-32</includeRegex>
      <width>HALF</width>
      <alignment>LEFT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
        <hudson.plugins.lastsuccessdescriptioncolumn.LastSuccessDescriptionColumn plugin="lastsuccessdescriptioncolumn@1.0"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>64bit</name>
      <includeRegex>unified-trunk-.*-package-64</includeRegex>
      <width>HALF</width>
      <alignment>RIGHT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.BuildButtonColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
        <hudson.plugins.lastsuccessdescriptioncolumn.LastSuccessDescriptionColumn plugin="lastsuccessdescriptioncolumn@1.0"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.TextSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>Other</name>
      <width>FULL</width>
      <alignment>CENTER</alignment>
      <text></text>
      <style>NONE</style>
    </hudson.plugins.sectioned__view.TextSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>32 Bit</name>
      <includeRegex>unified-trunk-.*(clean|main)-32</includeRegex>
      <width>HALF</width>
      <alignment>LEFT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastFailureColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
    <hudson.plugins.sectioned__view.ListViewSection>
      <jobNames>
        <comparator class="hudson.util.CaseInsensitiveComparator" reference="../../../hudson.plugins.sectioned__view.TextSection/jobNames/comparator"/>
      </jobNames>
      <jobFilters/>
      <name>64 Bit</name>
      <includeRegex>unified-trunk-(clean|main|debug).*64</includeRegex>
      <width>HALF</width>
      <alignment>RIGHT</alignment>
      <columns>
        <hudson.views.StatusColumn/>
        <hudson.views.WeatherColumn/>
        <hudson.views.JobColumn/>
        <hudson.views.LastSuccessColumn/>
        <hudson.views.LastFailureColumn/>
        <hudson.views.LastDurationColumn/>
        <de.fspengler.hudson.pview.ConsoleViewColumn plugin="hudson-pview-plugin@1.8"/>
      </columns>
    </hudson.plugins.sectioned__view.ListViewSection>
  </sections>
</hudson.plugins.sectioned__view.SectionedView>"""
    vxml = SectionedViewXML(sample)
    s = vxml.sections
    print(str(s))
    #print(isinstance(s[0], TextSection))
    print(s[1].includeRegex)
    s[1].set_include_regex(r"unified-4\.1\.x-.*-build-32")
    #print(s[1].get_xml())
    print(vxml.get_xml())



