"""Primitives that perform some common Jenkins operations that span the object heirarchy

The functions and classes defined in this module provide users with some pre-rolled custom
scripts that perform some common tasks that leverage a variety of tools and objects provided
by the PyJen API to accomplish their tasks (ie: these primitives typically make use of multiple
classes offered by the API and thus can't be easily attached or embedded within the public
PyJen API)
"""
from pyjen.jenkins import Jenkins


def find_view(jenkins_url, credentials, view_name):
    """Locates a view with a given name recursively across a Jenkins instance

    This helper function has knowledge of view plugins that support sub-views
    and thus recursively searches these sub-views for the requested view

    WARNING: This function can be quite slow when executed against a large Jenkins
    build farm with a large number of views and subviews.

    :param str jenkins_url: URL of the root Jenkins master
    :param tuple credentials: 2-tuple containing the user-name and password to authenticate with
    :param str view_name: name of the view to locate
    :returns: Reference to the view with the provided name, or None if the view doesn't exist
    :rtype: :class:`~.view.View`
    """
    from pyjen.plugins.nestedview import NestedView
    jen = Jenkins(jenkins_url, credentials)

    parent_view = jen.find_view(view_name)
    if parent_view is not None:
        return parent_view

    for cur_view in jen.views:
        if cur_view.type == NestedView.plugin_name:
            sub_view = cur_view.find_view(view_name)
            if sub_view is not None:
                return sub_view

    return None

if __name__ == "__main__":
    pass
