import importlib
from pyjen.plugins.pluginbase import pluginbase
import os

# Path where all PyJen plugins are stored
PYJEN_PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

from six import add_metaclass
from abc import ABCMeta, abstractproperty


@add_metaclass(ABCMeta)
class PluginBase(object):
    """Abstract base class common to all PyJen API plugins"""

    @abstractproperty
    def type(self):
        """The Jenkins plugin descriptive name, used when instantiating objects of that type

        :return: Jenkins plugin descriptive name, used when instantiating objects of that type
        :rtype: :func:`str`
        """
        raise NotImplementedError


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
    from pyjen.utils.pluginapi import PluginBase
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
    retval = []

    for loader, name, ispkg in pkgutil.walk_packages([path], "pyjen.plugins."):
        if not ispkg:
            retval.append(importlib.import_module(name))
            #cur_mod = loader.find_module(name).load_module(name)
            #retval.append(cur_mod)

    return retval

#------------------------------------
# OLD METHODS TO BE DEPRECATED


def get_xml_plugins():
    """Gets a list of all generic plugins used by Jenkins config.xml

    :returns:a list of all generic plugins used by Jenkins config.xml
    :rtype: :class:`list`
    """
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    retval = []
    for module in all_modules:
        public_classes = _extract_public_classes(module)
        view_classes = _extract_classes_of_type(public_classes, "pyjen.plugins.pluginbase.pluginbase")
        retval.extend(view_classes)

    return retval

def find_plugin_by_name(class_name):
    """Retrieves the PyJen class used to manage the Jenkins plugin of the specified name

    :param str class_name: the name of the Jenkins class to be managed
    :return: the PyJen class object, to instantiate to manage this Jenkins object
    """
    for plugin in get_xml_plugins():
        if plugin.type == class_name:
            return plugin

    raise PluginNotSupportedError("XML plugin {0} not found".format(class_name), class_name)










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
        # TODO: Rework this to use issubclass()
        for cur_baseclass in cur_class.__bases__:
            class_name = cur_baseclass.__module__ + "." + cur_baseclass.__name__
            if class_name == base_type:
                retval.append(cur_class)
                break
    return retval

if __name__ == "__main__": # pragma: no cover
    pass
