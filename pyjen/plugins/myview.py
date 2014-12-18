"""Primitives for interacting with Jenkins views of type 'MyView'"""
from pyjen.view import View


class MyView(View):
    """Interface to a view associated with a specific user

    Instances of this class are typically instantiated directly or indirectly through :py:meth:`pyjen.View.create`
    """
    type = "hudson.model.MyView"

    def __init__(self, data_io_controller, jenkins_master):
        """To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type data_io_controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master:
            Reference to Jenkins object associated with the master instance managing
            this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`
        """
        super(MyView, self).__init__(data_io_controller, jenkins_master)


if __name__ == "__main__":  # pragma: no cover
    pass
