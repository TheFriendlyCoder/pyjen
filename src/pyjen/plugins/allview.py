"""Class that interact with Jenkins views of type "AllView" """
from pyjen.view import View


class AllView(View):
    """view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or
    indirectly through :py:meth:`~.view.View.create`
    """
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.model.AllView"


PluginClass = AllView


if __name__ == "__main__":  # pragma: no cover
    pass
