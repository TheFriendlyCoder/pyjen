from pyjen.view import View
from pyjen.utils.view_xml import view_xml
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

    def clone_subview(self, existing_view, new_view_name):
        """Creates a clone of an existing view under this nested view

         :param existing_view: Instance of a PyJen view to be cloned
         :type existing_view: :class:`pyjen.view.View`
         :param str new_view_name: the new name for the view
         :returns: reference to new PyJen view object
         :rtype: :class:`pyjen.view.View`
         """
        retval = self.create_view(new_view_name, existing_view.type)
        vxml = view_xml(existing_view.config_xml)
        vxml.rename(new_view_name)
        retval.set_config_xml(vxml.get_xml())
        return retval

    def move_view(self, existing_view):
        """Moves an existing view to a new location

        NOTE: The original view object becomes obsolete after executing this operation
        :param existing_view: Instance of a PyJen view to be moved
        :returns: reference to new, relocated view object
        :rtype: :class:`pyjen.view.View"
        """
        new_view = self.clone_subview(existing_view, existing_view.name)
        existing_view.delete()
        return new_view
