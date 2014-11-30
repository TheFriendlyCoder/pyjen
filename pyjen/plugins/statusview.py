"""Primitives for operating on Jenkins views of type 'StatusView'"""
from pyjen.view import View


class StatusView(View):
    """Status view plugin"""
    type = "hudson.plugins.status_view.StatusView"

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(StatusView, self).__init__(controller, jenkins_master)


if __name__ == "__main__":  # pragma: no cover
    pass

