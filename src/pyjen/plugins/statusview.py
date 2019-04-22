"""Primitives for operating on Jenkins views of type 'StatusView'"""
from pyjen.view import View


class StatusView(View):
    """Interface to Jenkins views of type 'StatusView'"""

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.status_view.StatusView"


PluginClass = StatusView


if __name__ == "__main__":  # pragma: no cover
    pass
