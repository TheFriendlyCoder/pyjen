"""Primitives for working on Jenkins views of type 'SectionedView'"""
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.pluginapi import get_plugins, PluginBase, PluginXML
from pyjen.exceptions import PluginNotSupportedError
import xml.etree.ElementTree as ElementTree


class SectionedView(View):
    """Sectioned view plugin"""
    type = "hudson.plugins.sectioned_view.SectionedView"

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(SectionedView, self).__init__(controller, jenkins_master)

    @property
    def sections(self):
        vxml = SectionedViewXML(self.config_xml)
        return vxml.sections


class ListViewSection(PluginBase):
    """One of several 'section' types defined for a sectioned view

    Represents sections of type 'ListView'"""
    type = "hudson.plugins.sectioned_view.ListViewSection"

    def __init__(self, node):
        """Constructor"""
        self._root = node

    @property
    def include_regex(self):
        """Gets the regular expression associated with this section
        :returns: the regular expression associated with this section
        :rtype: :func:`str`
        """
        regex_node = self._root.find("includeRegex")
        if regex_node is None:
            return ""
        return regex_node.text

    @include_regex.setter
    def include_regex(self, new_regex):
        """Gets the regular expression associated with this section
        :returns: the regular expression associated with this section
        :rtype: :func:`str`
        """
        regex_node = self._root.find("includeRegex")
        if regex_node is None:
            regex_node = ElementTree.SubElement(self._root, 'includeRegex')
        regex_node.text = new_regex


class TextSection(PluginBase):
    """One of several 'section' types defined for a sectioned view

    Sections of this type contain simple descriptive text"""
    type = "hudson.plugins.sectioned_view.TextSection"

    def __init__(self, node):
        """Constructor"""
        self._node = node


class SectionedViewXML(ViewXML):
    """Abstraction for operating on raw config.xml data for a Jenkins view of type 'Sectioned View'"""
    def __init__(self, xml):
        """Constructor"""
        super(SectionedViewXML, self).__init__(xml)

    @property
    def sections(self):
        """Gets a list of all 'section' objects contained in this view"""
        sections_node = self._root.find('sections')

        retval = []
        for node in sections_node:
            configxml = ElementTree.tostring(node, "UTF-8").decode("utf-8")
            pluginxml = PluginXML(configxml)

            plugin_obj = None
            for plugin in get_plugins():
                if plugin.type == pluginxml.get_class_name():
                    plugin_obj = plugin(sections_node)

            if plugin_obj is None:
                raise PluginNotSupportedError("Sectioned view plugin {0} not found".format(pluginxml.get_class_name()),
                                              pluginxml.get_class_name())

            retval.append(plugin_obj)
        return retval


if __name__ == "__main__":  # pragma: no cover
    pass

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
    print(s[1].include_regex)
    s[1].include_regex = r"unified-4\.1\.x-.*-build-32"
    #print(s[1].get_xml())
    print(vxml.XML)



