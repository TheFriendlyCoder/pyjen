"""Class that interact with Jenkins views of type "AllView" """
from pyjen.view import View


class AllView(View):
    """Interface to a view which displays all jobs managed by this Jenkins instance

    Instances of this class are typically instantiated directly or indirectly through
    :py:meth:`~.view.View.create`
    """

    def __init__(self, url):
        """
        :param str url: REST API endpoint for this Jenkins view
        """
        super(AllView, self).__init__(url)


if __name__ == "__main__":  # pragma: no cover
    pass
