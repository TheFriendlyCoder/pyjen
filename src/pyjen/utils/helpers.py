"""Common API operations that may be used by various primitives"""
import json


def create_view(api, view_name, view_type):
    """Creates a new Jenkins view

    :param api:
        Jenkins REST API connection
    :param str view_name:
        Name of the view to create
    :param str view_type:
        Jenkins API compatible data type for a supported view
    :returns:
        clone of the given Jenkins API object, pre-configured for the new
        view
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
    return api.clone(api.url + "view/" + view_name)


if __name__ == "__main__":  # pragma: no cover
    pass
