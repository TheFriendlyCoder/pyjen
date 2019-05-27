"""Primitives for interacting with the PyJen plugin subsystem"""
import logging
from pkg_resources import iter_entry_points

# Every PyJen plugin must have a class registered with the following Python
# setup tools entrypoint
PLUGIN_ENTRYPOINT_NAME = "pyjen.plugins.v1.0"

# PyJen plugins are expected to be implemented as Python classes, with
# a static method named as shown below. This method is expected to return
# the name of the associated Jenkins plugin the Python class interacts with
PLUGIN_METHOD_NAME = "get_jenkins_plugin_name"


def find_plugin(plugin_name):
    """Locates the PyJen class associated with a given Jenkins plugin

    :param str plugin_name:
        Name of the Jenkins plugin to find the associated
    :returns:
        reference to the PyJen plugin class associated with the given Jenkins
        plugin, if one exists. If one doesn't exist, returns None.
    """
    formatted_plugin_name = plugin_name.replace("__", "_")

    log = logging.getLogger(__name__)

    supported_plugins = list()
    for cur_plugin in get_all_plugins():
        if getattr(cur_plugin, PLUGIN_METHOD_NAME)() == formatted_plugin_name:
            supported_plugins.append(cur_plugin)

    if not supported_plugins:
        return None

    if len(supported_plugins) > 1:
        log.warning("multiple plugins detected for specified Jenkins"
                    " object: %s. Using first match.", formatted_plugin_name)

    return supported_plugins[0]


def get_all_plugins():
    """Returns a list of all PyJen plugins installed on the system

    :returns: list of 0 or more installed plugins
    :rtype: :class:`list` of :class:`class`
    """
    log = logging.getLogger(__name__)
    # First load all libraries that are registered with the PyJen plugin API
    all_plugins = list()
    for entry_point in iter_entry_points(group=PLUGIN_ENTRYPOINT_NAME):
        all_plugins.append(entry_point.load())

    # Next, filter out those that don't support the current version of our API
    retval = list()
    for cur_plugin in all_plugins:
        if not hasattr(cur_plugin, PLUGIN_METHOD_NAME):
            log.debug(
                "Plugin %s does not expose the required %s static method.",
                cur_plugin.__module__,
                PLUGIN_METHOD_NAME)
            continue

        retval.append(cur_plugin)

    return retval


def instantiate_xml_plugin(node, parent):
    """Instantiates a PyJen XML plugin from an arbitrary XML node

    :param node:
        ElementTree node describing the plugin to be instantiated
    :param parent:
        ElementTree object that owns the plugin being instantiated
    :returns:
        Reference to the instantiated plugin, or None if the associated plugin
        isn't currently implemented in PyJen yet
    """
    log = logging.getLogger(__name__)
    plugin_class = find_plugin(node.tag)
    if not plugin_class:
        log.warning("Skipping unsupported plugin %s", node.tag)
        return None
    retval = plugin_class(node)
    retval.parent = parent
    return retval


if __name__ == "__main__":  # pragma: no cover
    pass
