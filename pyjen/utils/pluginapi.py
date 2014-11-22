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

if __name__ == "__main__": # pragma: no cover
    pass
