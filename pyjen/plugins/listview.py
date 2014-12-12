"""Primitives that operate on Jenkins views of type 'List'"""
from pyjen.view import View
from pyjen.user_params import JenkinsConfigParser
from pyjen.utils.datarequester import DataRequester
from pyjen.exceptions import InvalidJenkinsURLError


class ListView(View):
    """Class that encapsulates all Jenkins related 'view' information for views of type ListView

    Instances of this class are typically instantiated directly or indirectly through :py:meth:`pyjen.View.create`
    """
    type = "hudson.model.ListView"

    def __init__(self, data_io_controller, jenkins_master):
        """constructor

        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        """
        super(ListView, self).__init__(data_io_controller, jenkins_master)


if __name__ == "__main__":  # pragma: no cover
    pass
