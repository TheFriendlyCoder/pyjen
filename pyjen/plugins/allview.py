"""Class that interact with Jenkins views of type "AllView" """
from pyjen.view import View
from pyjen.user_params import JenkinsConfigParser
from pyjen.utils.datarequester import DataRequester
from pyjen.exceptions import InvalidJenkinsURLError


class AllView(View):
    """Interface to a view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or indirectly through
    :py:meth:`~.view.View.create`
    """
    type = "hudson.model.AllView"

    def __init__(self, data_io_controller, jenkins_master):
        """
        :param data_io_controller: IO interface to the Jenkins API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master: Reference to Jenkins master interface
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        """
        super(AllView, self).__init__(data_io_controller, jenkins_master)


if __name__ == "__main__":  # pragma: no cover
    pass
