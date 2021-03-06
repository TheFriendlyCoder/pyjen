"""Primitives that operate on Jenkins views of type 'List'"""
from pyjen.view import View


class ListView(View):
    """all Jenkins related 'view' information for views of type ListView"""

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """str: the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml
        """
        return "hudson.model.ListView"


PluginClass = ListView


if __name__ == "__main__":  # pragma: no cover
    pass
