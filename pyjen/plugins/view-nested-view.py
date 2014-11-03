from pyjen.view import View

class nested_view(View):
    """Nested view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(nested_view, self).__init__(controller, jenkins_master)

    def sub_views(self):
        #TODO: To be implemented
        return []