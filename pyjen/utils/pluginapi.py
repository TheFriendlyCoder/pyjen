import importlib
from pyjen.plugins.pluginbase import pluginbase
import os

# Path where all PyJen plugins are stored
PYJEN_PLUGIN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

from six import add_metaclass
from abc import ABCMeta, abstractproperty


@add_metaclass(ABCMeta)
class PluginBase(object):
    @abstractproperty
    def type(self):
        raise NotImplementedError


def get_plugins():
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    retval = []
    for module in all_modules:
        retval.extend(_extract_plugin_classes(module))
    return retval

def get_plugin_types():
    retval = []
    for p in get_plugins():
        retval.append(str(p.type))
    return retval

def _extract_plugin_classes(module):
    from pyjen.utils.pluginapi import PluginBase
    import inspect
    retval = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__.startswith("pyjen.plugins."):
            #print("{0} - {1}".format(name, str(obj)))
            #print(issubclass(obj, PluginBase))
            if issubclass(obj, PluginBase):
                retval.append(obj)
    #for attribute_name in dir(module):
    #    cur_attr = getattr(module, attribute_name)
    #    if inspect.isclass(cur_attr) and issubclass(cur_attr, PluginBase):
            #print(issubclass(cur_attr, PluginBase))
            #print(cur_attr)
    #        retval.append(cur_attr)

    return retval
#------------------------------------
# OLD METHODS TO BE DEPRECATED

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
    
    return find_plugin_by_name(plugin.get_class_name())

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

    #print("Found {0} items in {1}".format(len(retval), path))
    return retval

def get_view_plugins():
    """Returns a list of view plugins currently supported by the PyJen library
    :returns: a list of plugin names currently supported by the PyJen library
    :rtype: :func:`list`
    """
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    #print ("all modules: " + str(all_modules))
    retval = []
    for module in all_modules:
        #print("processing module " + str(module))
        public_classes = _extract_public_classes(module)
        view_classes = _extract_classes_of_type(public_classes, "pyjen.view.View")

        #print("adding classes " + str(view_classes))
        retval.extend(view_classes)

    #print("Supported plugins: " + str(retval))
    return retval

def get_job_plugins():
    """Returns a list off job plugins currently supported by the PyJen library
    :returns: a list of plugin names currently supported by the PyJen library
    :rtype: :func:`list`
    """
    all_modules = _load_modules(PYJEN_PLUGIN_FOLDER)
    retval = []
    for module in all_modules:
        public_classes = _extract_public_classes(module)
        job_classes = _extract_classes_of_type(public_classes, "pyjen.job.Job")
        retval.extend(job_classes)

    return retval

class PluginNotSupportedError(NotImplementedError):
    """Basic extension to the NotImplementedError with details about which plugin was not found"""
    def __init__(self, message, plugin_name):
        """Constructor

        :param str message: desciption of the error
        :param str plugin_name: the class name / type of the plugin that was not found
        """
        super(PluginNotSupportedError, self).__init__()
        self._message = message
        self._plugin_name = plugin_name

    def __str__(self):
        return self._message

    @property
    def message(self):
        return self._message

    @property
    def plugin_name(self):
        return self._plugin_name

def find_view_plugin_by_name(class_name):
    """Given a Jenkins plugin class name, returns an instance of the PyJen class that manages it

    An exception will be raised if no supporting PyJen plugin can be found

    :param str class_name: the name of the Jenkins plugin to find
    :return: an instance of the PyJen plugin class responsible for managing Jenkins plugins of the given type
    """

    for plugin in get_view_plugins():
        if plugin.type == class_name:
            #print("Found " + plugin.type)
            #mod = importlib.import_module(plugin.__module__)
            #classobj = getattr(mod, plugin.__name__)
            #return classobj
            return plugin

    raise PluginNotSupportedError("View plugin {0} not found".format(class_name), class_name)

def find_job_plugin_by_name(class_name):
    """locates the class for a Jenkins plugin in the PyJen plugin repo by name

    :param str plugin_name: The name of the plugin to find
    :returns: Instance of the class that manages the given plugin
    :rtype: :py:mod:`pyjen.plugins.pluginbase`
    """
    for plugin in get_job_plugins():
        if plugin.type == class_name:
            return plugin

    raise PluginNotSupportedError("Job plugin {0} not found".format(class_name), class_name)

def find_view_plugin(xml):
    """Loads the PyJen class used to manage the plugin described by the given XML snippet

    :param str xml: XML data, typically read from a Jenkins config.xml file, associated with the plugin to be found
    :return: an instance of the PyJen plugin classs responsible for managing Jenkins plugins of the given type
    """
    plugin = pluginbase(xml)

    return find_view_plugin_by_name(plugin.get_class_name())

def find_job_plugin(xml):
    """locates the class for a Jenkins plugin in the PyJen plugin repo based on XML configuration data

    :param str xml: the xml representation of the plugin configuration properties as found in the associated config.xml
    :returns: The PyJen plugin class used to manage the given plugin. The caller can then instantiate an instance of the
        class as needed.
    :rtype: :py:mod:`pyjen.plugins.pluginbase`
    """
    plugin = pluginbase(xml)

    return find_job_plugin_by_name(plugin.get_class_name())


if __name__ == "__main__": # pragma: no cover
    pass
