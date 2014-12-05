"""Primitives for working with Jenkins views of type 'NestedView'"""
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.exceptions import NestedViewCreationError
import json


class NestedView(View):
    """Interface to Jenkins views of type "NestedView"

    Views of this type contain other views as sub-views
    """

    type = "hudson.plugins.nested_view.NestedView"

    def __init__(self, controller, jenkins_master):
        """
        To instantiate an instance of this class using auto-generated
        configuration parameters, see the :py:func:`easy_connect` method

        :param controller:
            class capable of handling common HTTP IO requests sent by this
            object to the Jenkins REST API
        :type controller: :class:`~.utils.datarequester.DataRequester`
        :param jenkins_master:
            Reference to Jenkins object associated with the master instance managing
            this job
        :type jenkins_master: :class:`~.jenkins.Jenkins`        """
        super(NestedView, self).__init__(controller, jenkins_master)

    @property
    def views(self):
        """Gets all views contained within this view

        To get a recursive list of all child views and their children use :py:func:`all_views`.

        :returns: list of all views contained within this view
        :rtype: :class:`list`
        """
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
        """Gets all views contained within this view and it's children, recursively

        :returns: list of all views contained within this view and it's children, recursively
        :rtype: :class:`list`
        """
        temp = self.views

        retval = []
        for cur_view in temp:
            if cur_view.contains_views:
                retval.extend(cur_view.all_views)

        retval.extend(temp)
        return retval

    @property
    def contains_views(self):
        """Indicates whether this view type supports sub-views

        :returns: True if this class contains other views, otherwise False
        :rtype: :class:`bool`
        """
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

        for cur_view in raw_views:
            if cur_view['name'] == view_name:
                new_io_obj = self._controller.clone(cur_view['url'])
                return View.create(new_io_obj, self._master)
                
        raise NestedViewCreationError("Failed to create nested view " + view_name + " under " + self.name)

    def clone_subview(self, existing_view, new_view_name):
        """Creates a clone of an existing view under this nested view

         :param existing_view: Instance of a PyJen view to be cloned
         :type existing_view: :class:`~.view.View`
         :param str new_view_name: the new name for the view
         :returns: reference to new PyJen view object
         :rtype: :class:`~.view.View`
         """
        retval = self.create_view(new_view_name, existing_view.type)
        vxml = ViewXML(existing_view.config_xml)
        vxml.rename(new_view_name)
        retval.set_config_xml(vxml.XML)
        return retval

    def move_view(self, existing_view):
        """Moves an existing view to a new location

        NOTE: The original view object becomes obsolete after executing this operation

        :param existing_view: Instance of a PyJen view to be moved
        :type existing_view: :class:`~.view.View`
        :returns: reference to new, relocated view object
        :rtype: :class:`~.view.View"
        """
        new_view = self.clone_subview(existing_view, existing_view.name)
        existing_view.delete()
        return new_view


if __name__ == "__main__":  # pragma: no cover
    pass
