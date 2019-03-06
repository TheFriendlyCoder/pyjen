"""Primitives for interacting with the PyJen plugin subsystem"""
import logging
from pkg_resources import iter_entry_points

# Every PyJen plugin must have a class registered with the following Python
# setup tools entrypoint
PLUGIN_ENTRYPOINT_NAME = "pyjen.plugins"

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
    log = logging.getLogger(__name__)
    all_plugins = list()
    for entry_point in iter_entry_points(group=PLUGIN_ENTRYPOINT_NAME):
        all_plugins.append(entry_point.load())

    supported_plugins = list()
    for cur_plugin in all_plugins:
        if not hasattr(cur_plugin, PLUGIN_METHOD_NAME):
            log.debug(
                "Plugin %s does not expose the required %s static method.",
                cur_plugin.__module__,
                PLUGIN_METHOD_NAME)
            continue

        if getattr(cur_plugin, PLUGIN_METHOD_NAME)() == plugin_name:
            supported_plugins.append(cur_plugin)

    if not supported_plugins:
        return None

    if len(supported_plugins) > 1:
        log.warning("multiple plugins detected for specified Jenkins"
                    " object: %s. Using first match.", plugin_name)

    return supported_plugins[0]


if __name__ == "__main__":  # pragma: no cover
    pass
