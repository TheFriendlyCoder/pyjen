"""Primitives that operate on Jenkins views of type 'List'"""
from pyjen.view import View


class ListView(View):
    """Class that encapsulates all Jenkins related 'view' information for views of type ListView

    Instances of this class are typically instantiated directly or indirectly through :py:meth:`pyjen.View.create`
    """

    def __init__(self, url):
        """constructor

        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param obj data_io_controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        """
        super(ListView, self).__init__(url)


if __name__ == "__main__":  # pragma: no cover
    pass
