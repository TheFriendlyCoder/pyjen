"""Misc helper methods shared across the library"""
import json


def create_view(api, view_name, view_class):
    """Creates a new view on the Jenkins dashboard

    :param api:
        Jenkins rest api connection to use for creation of the view`
    :param str view_name:
        the name for this new view
        This name should be unique, different from any other views currently
        managed by the Jenkins instance
    :param view_class:
        PyJen plugin class associated with the type of view to be created
    """
    view_type = view_class.get_jenkins_plugin_name()
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


def create_job(api, job_name, job_class):
    """Creates a new job on the Jenkins dashboard

    :param api:
        Jenkins rest api connection to use for creation of the view`
    :param str job_name:
        the name for this new job
        This name should be unique, different from any other jobs currently
        managed by the Jenkins instance
    :param job_class:
        PyJen plugin class associated with the type of job to be created
    """
    headers = {'Content-Type': 'text/xml'}

    params = {
        "name": job_name
    }

    xml_config = job_class.template_config_xml()
    data = xml_config

    args = {
        'data': data,
        'params': params,
        'headers': headers
    }

    api.post(api.url + 'createItem', args)
