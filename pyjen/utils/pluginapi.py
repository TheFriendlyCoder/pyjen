import importlib
from pyjen.plugins.pluginbase import pluginbase
import os

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
    
    full_plugin_name = "pyjen.plugins." + plugin.get_module_name()
    
    plugin_module = importlib.import_module(full_plugin_name)

    plugin_class = getattr(plugin_module, plugin.get_module_name())
    
    return plugin_class(xml)

def find_job_plugin(xml):
    """locates the class for a Jenkins plugin in the PyJen plugin repo based on XML configuration data

    :param str xml: the xml representation of the plugin configuration properties as found in the associated config.xml
    :returns: The PyJen plugin class used to manage the given plugin. The caller can then instantiate an instance of the
        class as needed.
    :rtype: :py:mod:`pyjen.plugins.pluginbase`
    """
    plugin = pluginbase(xml)

    return find_job_plugin_by_name(plugin.get_module_name())

def find_job_plugin_by_name(plugin_name):
    """locates the class for a Jenkins plugin in the PyJen plugin repo by name

    :param str plugin_name: The name of the plugin to find
    :returns: Instance of the class that manages the given plugin
    :rtype: :py:mod:`pyjen.plugins.pluginbase`
    """
    full_plugin_name = "pyjen.plugins.job-" + plugin_name

    plugin_module = importlib.import_module(full_plugin_name)

    return getattr(plugin_module, plugin_name.replace("-", "_"))

def find_view_plugin(xml):
    plugin = pluginbase(xml)

    full_plugin_name = "pyjen.plugins.view." + plugin.get_module_name()

    plugin_module = importlib.import_module(full_plugin_name)

    return getattr(plugin_module, plugin.get_class_name())

def list_job_plugins():
    """Returns a list off job plugins currently supported by the PyJen library
    :returns: a list of plugin names currently supported by the PyJen library
    :rtype: :func:`list`
    """
    path_to_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))
    plugin_files = os.listdir(path_to_plugins)

    retval = []
    for file in plugin_files:
        if os.path.isfile(os.path.join(path_to_plugins, file)) and file.startswith("job-"):
            retval.append(os.path.splitext(file)[0].replace("job-", ""))

    return retval

def list_view_plugins():
    """Returns a list of view plugins currently supported by the PyJen library
    :returns: a list of plugin names currently supported by the PyJen library
    :rtype: :func:`list`
    """
    path_to_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins", "view"))
    plugin_files = os.listdir(path_to_plugins)

    retval = []
    for file in plugin_files:
        if file != "__init__.py" and os.path.isfile(os.path.join(path_to_plugins, file)):
            full_plugin_name = "pyjen.plugins.view."+os.path.splitext(file)[0]
            plugin_module = importlib.import_module(full_plugin_name)
            plugin_name = os.path.splitext(file)[0]
            plugin_name = plugin_name.replace("view-", "")
            plugin_name = plugin_name.replace("-", "_")
            plugin_class = getattr(plugin_module, plugin_name)

            retval.append(plugin_class.type)

    return retval

if __name__ == "__main__": # pragma: no cover
    import pyjen
    path_to_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins", "view"))
    #print(path_to_plugins)
    #from pyjen.plugins.view import *
    import pkgutil
    for l, n, p in pkgutil.walk_packages([path_to_plugins]):
        #print ("{0} - {1} - {2}".format(l, n, p))
        mod = l.find_module(n).load_module(n)
        #print(dir(mod.nested_view))
        for z in dir(mod):
            if not z.startswith("__"):
                #print ("processing " + z)
                tempattr = getattr(mod, z)
                #print ("attribute {0}".format(tempattr))
                #print ("Type of thing is {0}".format(type(mod)))
                if hasattr(tempattr, "__bases__"):
                    for i in tempattr.__bases__:
                        class_name = i.__module__ + "." + i.__name__
                        #print ("base class name is " + class_name)
                        if class_name == "pyjen.view.View":
                            print ("Found plugin class {0}".format(tempattr))
        exit()
    print("done")
