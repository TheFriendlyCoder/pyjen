from pyjen.view import View

class sectioned_view(View):
    """Sectioned view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(sectioned_view, self).__init__(controller, jenkins_master)

    type = "hudson.plugins.sectioned_view.SectionedView"