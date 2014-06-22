import unittest
from pyjen.utils.view_xml import view_xml
import pytest

class view_xml_tests(unittest.TestCase):
    """Tests for parsing data from a view's config.xml"""
    def test_get_type(self):
        config_xml = """
        <hudson.model.ListView>
            <name>TestView</name>
            <filterExecutors>false</filterExecutors>
            <filterQueue>false</filterQueue>
            <properties class="hudson.model.View$PropertyList"/>
            <jobNames>
                <comparator class="hudson.util.CaseInsensitiveComparator"/>
                <string>test_job_1</string>
            </jobNames>
            <jobFilters/>
            <columns>
                <hudson.views.StatusColumn/>
                <hudson.views.WeatherColumn/>
                <hudson.views.JobColumn/>
                <hudson.views.LastSuccessColumn/>
                <hudson.views.LastFailureColumn/>
                <hudson.views.LastDurationColumn/>
                <hudson.views.BuildButtonColumn/>
            </columns>
            <recurse>false</recurse>
        </hudson.model.ListView>"""
        
        vxml = view_xml(config_xml)
        self.assertEqual(vxml.get_type(), "hudson.model.ListView")
        
    def test_get_type_sectioned_view(self):
        config_xml = """
        <hudson.plugins.sectioned__view.SectionedView plugin="sectioned-view@1.18">
            <name>test_view</name>
            <filterExecutors>false</filterExecutors>
            <filterQueue>false</filterQueue>
            <properties class="hudson.model.View$PropertyList"/>
            <sections>
                <hudson.plugins.sectioned__view.TextSection>
                    <jobNames>
                        <comparator class="hudson.util.CaseInsensitiveComparator"/>
                    </jobNames>
                    <jobFilters/>
                    <name>Hello World</name>
                    <width>FULL</width>
                    <alignment>CENTER</alignment>
                    <text/>
                    <style>NONE</style>
                </hudson.plugins.sectioned__view.TextSection>
                </sections>
            </hudson.plugins.sectioned__view.SectionedView>"""
        
        vxml = view_xml(config_xml)
        # NOTE: Here the plugin name is sectioned_view but the Jenkins config XML
        # seems to double up any underscores in the raw XML. These double underscores
        # are expected to be fixed when using API methods like get_type
        self.assertEqual(vxml.get_type(), "hudson.plugins.sectioned_view.SectionedView")
            
            
if __name__ == "__main__":
    pytest.main()