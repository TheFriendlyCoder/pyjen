"""Class that interact with Jenkins views of type "AllView" """
from pyjen.view import View


class AllView(View):
    """view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or
    indirectly through :py:meth:`~.view.View.create`

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(AllView, self).__init__(api)

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "allview"


PluginClass = AllView


if __name__ == "__main__":  # pragma: no cover
    pass
