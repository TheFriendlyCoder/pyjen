"""Primitives for interacting with Jenkins views of type 'MyView'"""
from pyjen.view import View


class MyView(View):
    """Interface to a view associated with a specific user

    Instances of this class are typically instantiated directly or indirectly
    through :py:meth:`pyjen.View.create`
    """

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.model.MyView"


PluginClass = MyView


if __name__ == "__main__":  # pragma: no cover
    pass
