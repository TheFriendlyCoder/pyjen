"""Class that interact with Jenkins views of type "AllView" """
from pyjen.view import View


class AllView(View):
    """Interface to a view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or indirectly through
    :py:meth:`~.view.View.create`
    """
    type = "hudson.model.AllView"

    def __init__(self, url):
        """
        :param data_io_controller: IO interface to the Jenkins API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master: Reference to Jenkins master interface
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        """
        super(AllView, self).__init__(url)


if __name__ == "__main__":  # pragma: no cover
    pass
