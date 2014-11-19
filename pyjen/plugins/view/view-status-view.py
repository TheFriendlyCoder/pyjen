from pyjen.view import View

class status_view(View):
    """Status view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(status_view, self).__init__(controller, jenkins_master)

    @property
    def type(self):
        return "hudson.plugins.status__view.StatusView"