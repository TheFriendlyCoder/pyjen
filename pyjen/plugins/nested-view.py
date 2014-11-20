from pyjen.view import View
from pyjen.exceptions import NestedViewCreationError
import json

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
            tview = View.create(new_io_obj, self._master)
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


    type = "hudson.plugins.nested_view.NestedView"

    @property
    def contains_views(self):
        return True

    def create_view(self, view_name, view_type):
        """Creates a new sub-view within this nested view

        :param str view_name: name of the new sub-view to create
        :param str view_type: data type for newly generated view
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }

        args = {}
        args['data'] = data
        args['headers'] = headers

        self._controller.post('/createView', args)

        # Load a pyjen.View object with the new view
        data = self._controller.get_api_data()

        raw_views = data['views']
        retval = []

        for cur_view in raw_views:
            if cur_view['name'] == view_name:
                new_io_obj = self._controller.clone(cur_view['url'])
                return View.create(new_io_obj, self._master)
                
        raise NestedViewCreationError("Failed to create nested view " + view_name + " under " + self.name)