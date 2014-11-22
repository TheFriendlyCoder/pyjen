import os

import xml.etree.ElementTree as ElementTree
from pyjen.utils.plugin_base import PluginBase

# Path where all PyJen plugins are stored
PYJEN_PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))






class PluginXML(object):
    """Class used to process XML configuration information associated with Jenkins plugins"""
    def __init__(self, xml):
        """constructor

        :param str xml: the XML sub-tree defining the properties of this plugin
        """
        self._root = ElementTree.fromstring(xml)

    def get_module_name(self):
        """Gets the name of the plugin

        :returns: the plugin name
        :rtype: :func:`str`
        """
        attr = self._root.attrib['plugin']
        parts = attr.split('@')
        return parts[0]

    def get_class_name(self):
        """Gets the Java class name of the plugin

        :returns: the Java class name
        :rtype: :func:`str`
        """

        if "class" in self._root.attrib:
            temp = self._root.attrib['class']
        else:
            temp = self._root.tag

        # NOTE: For some reason, class names with underscores in them are represented in
        # the config.xml with double-underscores. We need to undo this obfuscation here
        return temp.replace("__", "_")


    def get_version(self):
        """Gets the version of the plugin

        :returns: the plugin version
        :rtype: :func:`str`
        """
        attr = self._root.attrib['plugin']
        parts = attr.split('@')
        return parts[1]

def get_plugins():
    """Returns list of classes for all plugins supported by PyJen

    :returns: list of classes for all PyJen plugins
    :rtype: :func:`list` of :mod:`pyjen.utils.pluginapi.PluginBase` derived objects
    """
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    retval = []
    for module in all_modules:
        retval.extend(_get_plugin_classes(module))
    return retval

def _get_plugin_classes(module):
    """Gets a list of all PyJen plugins from a given Python module
    :param module: A Python module object to be processed
    :returns: list of classes found within the given module that implement PyJen plugin interfaces
    :rtype: :func:`list` of :mod:`pyjen.utils.pluginapi.PluginBase` objects
    """
    import inspect
    retval = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__.startswith("pyjen.plugins."):
            if issubclass(obj, PluginBase):
                retval.append(obj)

    return retval

def _load_modules(path):
    """Gets a list of all modules found in a given path

    :param str path: path containing Python modules to be loaded
    :return: :class:`list` of objects of type 'module' found in the specified folder
    :rtype: :class:`list`
    """
    import pkgutil
    import importlib
    retval = []

    for loader, name, ispkg in pkgutil.walk_packages([path], "pyjen.plugins."):
        if not ispkg:
            retval.append(importlib.import_module(name))
            #cur_mod = loader.find_module(name).load_module(name)
            #retval.append(cur_mod)

    return retval

if __name__ == "__main__": # pragma: no cover
    for i in get_plugins():
        print(i.type)
    pass
