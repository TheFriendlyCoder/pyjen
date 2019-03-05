"""Primitives for operating on Jenkins views of type 'StatusView'"""
from pyjen.view import View


class StatusView(View):
    """Interface to Jenkins views of type 'StatusView'

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(StatusView, self).__init__(api)

    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "statusview"


PluginClass = StatusView


if __name__ == "__main__":  # pragma: no cover
    pass
