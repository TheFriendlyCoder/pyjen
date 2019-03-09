"""Class that interact with Jenkins views of type "AllView" """
import logging
from pyjen.view import View


class AllView(View):
    """view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or
    indirectly through :py:meth:`~.view.View.create`

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    :param parent:
        PyJen object that "owns" this view. Typically this is a reference to
        the :class:`pyjen.jenkins.Jenkins` object for the current Jenkins
        instance but in certain cases this may be a different object like
        a :class:`pyjen.plugins.nestedview.NestedView`.

        The parent object is expected to expose a method named `create_view`
        which can be used to clone instances of this view.
    """

    def __init__(self, api, parent):
        super(AllView, self).__init__(api, parent)
        self._log = logging.getLogger(__name__)

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
