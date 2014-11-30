from pyjen.utils.pluginapi import *
import unittest
import pytest

class PluginXmlTests(unittest.TestCase):
    def test_get_module_name(self):
        expected_module_name = "nested-view"
        xml = '<test plugin="{0}@123"/>'.format(expected_module_name)
        ob = PluginXML(xml)
        self.assertEqual(ob.get_module_name(), expected_module_name)

    def test_get_version(self):
        expected_module_version = "123"
        xml = '<test plugin="nested-view@{0}"/>'.format(expected_module_version)
        ob = PluginXML(xml)
        self.assertEqual(ob.get_version(), expected_module_version)

    def test_get_class_name_from_attribute(self):
        expected_module_name = "nested-view"
        xml = '<test class="{0}"/>'.format(expected_module_name)
        ob = PluginXML(xml)
        self.assertEqual(ob.get_class_name(), expected_module_name)

    def test_get_class_name_from_node(self):
        expected_module_name = "nested-view"
        xml = '<{0}/>'.format(expected_module_name)
        ob = PluginXML(xml)
        self.assertEqual(ob.get_class_name(), expected_module_name)

    def test_get_class_name_reformat(self):
        original_module_name = "hudson.plugin.nested__view.NestedView"
        expected_module_name = "hudson.plugin.nested_view.NestedView"
        xml = '<{0}/>'.format(original_module_name)
        ob = PluginXML(xml)
        self.assertEqual(ob.get_class_name(), expected_module_name)

class PluginAPITests(unittest.TestCase):
    def test_all_plugins(self):
        all_plugins = get_plugins()

        # List of all plugins supported by PyJen atm
        expected_plugins = [
            "hudson.model.AllView",
            "project",
            "hudson.model.ListView",
            "maven2-moduleset",
            "hudson.model.MyView",
            "hudson.plugins.nested_view.NestedView",
            "hudson.plugins.sectioned_view.SectionedView",
            "hudson.plugins.sectioned_view.TextSection",
            "hudson.plugins.sectioned_view.ListViewSection",
            "hudson.plugins.status_view.StatusView",
            "hudson.scm.NullSCM",
            "hudson.scm.SubversionSCM",
            "hudson.plugins.buildblocker.BuildBlockerProperty"]

        self.assertEqual(len(all_plugins), len(expected_plugins))
        for cur_plugin in all_plugins:
            self.assertIn(cur_plugin.type, expected_plugins)
            expected_plugins.remove(cur_plugin.type)

        self.assertEquals(len(expected_plugins), 0, "One or more plugins not found: " + str(expected_plugins))

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
