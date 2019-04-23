"""Primitives for working with Jenkins views of type 'NestedView'"""
from pyjen.view import View
from pyjen.utils.viewxml import ViewXML
from pyjen.utils.helpers import create_view


class NestedView(View):
    """all Jenkins related 'view' information for views of type NestedView

    Instances of this class are typically instantiated directly or indirectly
    through :py:meth:`pyjen.View.create`
    """

    @property
    def views(self):
        """Gets all views contained within this view, non-recursively

        To get a recursive list of all child views and their children use
        :py:meth:`all_views`.

        :returns: list of all views contained within this view
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()

        data = self._api.get_api_data()

        for cur_view in data['views']:
            retval.append(View.instantiate(cur_view, self._api))

        return retval

    def find_view(self, view_name):
        """Attempts to locate a sub-view under this nested view by name

        NOTE: Seeing as how view names need only be unique within a single
        parent view, there may be multiple nested views with the same name.
        To reflect this requirement this method will return a list of views
        nested within this one that have the name given. If the list is empty
        then there are no matches for the given name anywhere in this
        view's sub-tree.

        :param str view_name: the name of the sub-view to locate
        :returns: List of 0 or more views with the given name
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()
        for cur_view in self.all_views:
            if cur_view.name == view_name:
                retval.append(cur_view)

        return retval

    @property
    def all_views(self):
        """Gets all views contained within this view, recursively

        :returns:
            list of all views contained within this view and it's children,
            recursively
        :rtype: :class:`list` of :class:`pyjen.view.View`
        """
        retval = list()
        for cur_view in self.views:

            retval.append(cur_view)

            # See if our current view is, itself a nested view. If so then
            # recurse into it appending all the views contained therein as well
            if isinstance(cur_view, NestedView):
                retval.extend(cur_view.all_views)

        return retval

    def create_view(self, view_name, view_type):
        """Creates a new sub-view within this nested view

        :param str view_name:
            name of the new sub-view to create
        :param view_type:
            PyJen plugin class associated with the view type to create
        :returns: reference to the newly created view
        :rtype: :class:`pyjen.view.View`
        """
        new_api = create_view(self._api, view_name, view_type.get_jenkins_plugin_name())
        retval = view_type(new_api)
        assert retval.name == view_name
        return retval

    def clone_view(self, source_view, new_view_name):
        """Make a copy of a view with the specified name under this nested view

        :param source_view: view to be cloned
        :type source_view: :class:`pyjen.view.View`
        :param str new_view_name:
            name to give the newly created view
        :return: reference to the created view
        :rtype: :class:`~.view.View`
        """
        vxml = ViewXML(source_view.config_xml)
        new_view = self.create_view(new_view_name, source_view.__class__)

        vxml.rename(new_view_name)
        new_view.config_xml = vxml.xml
        return new_view

    def move_view(self, existing_view):
        """Moves an existing view under this nested view

        NOTE: The original view object becomes obsolete after executing this
        operation

        :param existing_view: Instance of a PyJen view to be moved
        :type existing_view: :class:`pyjen.view.View`
        :returns: reference to new, relocated view object
        :rtype: :class:`pyjen.view.View`
        """
        # TODO: Consider updating state of original view object here
        #       instead of returning a copy of a new view
        # TODO: Consider, if I can't get the tests for this working to
        #       just remove this helper completely
        new_view = self.create_view(
            existing_view.name, existing_view.__class__)
        new_view.config_xml = existing_view.config_xml
        existing_view.delete()
        return new_view

    # --------------------------------------------------------------- PLUGIN API
    @staticmethod
    def get_jenkins_plugin_name():
        """Gets the name of the Jenkins plugin associated with this PyJen plugin

        This static method is used by the PyJen plugin API to associate this
        class with a specific Jenkins plugin, as it is encoded in the config.xml

        :rtype: :class:`str`
        """
        return "hudson.plugins.nested_view.NestedView"


PluginClass = NestedView


if __name__ == "__main__":  # pragma: no cover
    pass
