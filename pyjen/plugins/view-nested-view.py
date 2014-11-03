from pyjen.view import View

class nested_view(View):
    """Nested view plugin"""

    def __init__(self, controller, jenkins_master):
        """constructor

        :param str controller: data processing object to manage interaction with Jenkins API
        """
        super(nested_view, self).__init__(controller, jenkins_master)

    @property
    def views(self):
        data = self._controller.get_api_data()

        raw_views = data['views']
        retval = []

        for cur_view in raw_views:
            new_io_obj = self._controller.clone(cur_view['url'])
            tview = View.create(new_io_obj, self)
            retval.append(tview)

        return retval

    @property
    def all_views(self):
        temp = self.views

        retval = []
        for cur_view in temp:
            if cur_view.contains_views:
                retval.extend(cur_view.all_views)

        retval.extend(temp)
        return retval


    @property
    def type(self):
        return "nested-view"

    @property
    def contains_views(self):
        return True