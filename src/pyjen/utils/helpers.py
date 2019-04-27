import json


def create_view(api, view_name, view_type):
    """Creates a new view on the Jenkins dashboard

    :param api:
        Jenkins rest api connection to use for creation of the view`
    :param str view_name:
        the name for this new view
        This name should be unique, different from any other views currently
        managed by the Jenkins instance
    :param str view_type:
        type of view to create
        must match one or more of the available view types supported by this
        Jenkins instance.
        See :py:meth:`~.view.View.supported_types` for a list of
        supported view types.
    """
    view_type = view_type.replace("__", "_")
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "name": view_name,
        "mode": view_type,
        "Submit": "OK",
        "json": json.dumps({"name": view_name, "mode": view_type})
    }

    args = {
        'data': data,
        'headers': headers
    }

    api.post(api.url + 'createView', args)
