import importlib
from pyjen.plugins.pluginbase import pluginbase

def find_plugin(xml):
    """Dynamically locates the class for a Jenkins plugin
    
    :param str xml: the xml representation of the plugin configuration properties
        as found in the associated config.xml
    :returns:
        An instance of the appropriate plugin, initialized with
        the properties provided in the given xml snippet
    :rtype: :py:mod:`pyjen.plugins.pluginbase`
    """
    plugin = pluginbase(xml)
    
    full_plugin_name = "pyjen.plugins." + plugin.get_name()
    
    plugin_module =  importlib.import_module(full_plugin_name)

    plugin_class = getattr(plugin_module, plugin.get_name())
    
    return plugin_class(xml)