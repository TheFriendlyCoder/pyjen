import importlib
from pyjen.plugins.pluginbase import pluginbase
import os

# Path where all PyJen plugins are stored
PYJEN_PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

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



def _extract_public_classes(module):
    """Given an object of type 'module', extract all public 'class' type objects contained therein

    :param module: The module containing classes to be processed
    :return: :class:`list` of 'class' objects
    :rtype: :class:`list`
    """
    import inspect
    retval = []
    for attribute_name in dir(module):
        if not attribute_name.startswith("_"):
            cur_attr = getattr(module, attribute_name)
            if inspect.isclass(cur_attr):
                retval.append(cur_attr)

    return retval

def _extract_classes_of_type(classes, base_type):
    """Given a list of class objects, extract those which implement / derive from a given base class type

    :param list classes: list of 1 or more objects of type 'class' to be analysed
    :param str base_type: the descriptive name of the base class of all classes to be found
    :return: :class:`list` of 'class' objects that inherit from a base class of type base_type
    :rtype: :class:`list`
    """
    retval = []
    for cur_class in classes:
        for cur_baseclass in cur_class.__bases__:
            class_name = cur_baseclass.__module__ + "." + cur_baseclass.__name__
            if class_name == base_type:
                retval.append(cur_class)
                break
    return retval

def _load_modules(path):
    """Gets a list of all modules found in a given path

    :param str path: path containing Python modules to be loaded
    :return: :class:`list` of objects of type 'module' found in the specified folder
    :rtype: :class:`list`
    """
    import pkgutil
    retval = []
    for loader, name, ispkg in pkgutil.walk_packages([path]):
        if not ispkg:
            retval.append(loader.find_module(name).load_module(name))

    return retval

def get_view_plugins():
    """Returns a list of view plugins currently supported by the PyJen library
    :returns: a list of plugin names currently supported by the PyJen library
    :rtype: :func:`list`
    """
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    retval = []
    for module in all_modules:
        public_classes = _extract_public_classes(module)
        view_classes = _extract_classes_of_type(public_classes, "pyjen.view.View")
        retval.extend(view_classes)

    return retval

if __name__ == "__main__": # pragma: no cover
    pass
