"""Base class for all objects that interact with the Jenkins REST API"""
import logging
import json
import xml.etree.ElementTree as ElementTree
import requests
from requests.exceptions import InvalidHeader
from six.moves import urllib_parse


class JenkinsAPI(object):
    """Abstraction around the raw Jenkins REST API

    :param str url:
        URL of the Jenkins REST API endpoint to manage
    :param tuple creds:
        username and password pair to authenticate with when accessing
        the REST API
    :param ssl_cert:
        Either a boolean controlling SSL verification, or a path to a cert
        authority bundle to use for SSL verification.
    ."""

    def __init__(self, url, creds, ssl_cert):
        self._log = logging.getLogger(__name__)

        self._url = url.rstrip("/\\") + "/"
        self._creds = creds
        self._ssl_cert = ssl_cert

        self._jenkins_root_url = self._url

        # Internal data members used for caching certain API response data
        # to improve performance
        self._crumb_cache = None
        self._jenkins_headers_cache = None

    def __str__(self):
        """String representation of the job"""
        return self.url

    def __repr__(self):
        """Encoded state of the job usable for serialization"""
        return "({0}: {1})".format(type(self), self.url)

    def clone(self, api_url):
        """Creates a copy of this instance, for a new endpoint URL

        :param str api_url:
            URL for the new REST API endpoint to be managed
        :returns:
            newly created JenkinsAPI
        :rtype: :class:`~.utils.jenkins_api.JenkinsAPI`
        """
        retval = JenkinsAPI(api_url, self._creds, self._ssl_cert)
        retval._jenkins_root_url = self._jenkins_root_url  # pylint: disable=protected-access
        return retval

    @property
    def url(self):
        """Gets the URL for the REST API endpoint managed by this object

        NOTE: The URL returned by this property is guaranteed to end with a
        trailing slash character

        :rtype: :class:`str`"""
        return self._url

    @property
    def root_url(self):
        """URL of the main Jenkins dashboard associated with the current object

        NOTE: The URL returned by this property is guaranteed to end with a
        trailing slash character

        :rtype: :class:`str`
        """
        return self._jenkins_root_url

    @property
    def jenkins_headers(self):
        """HTTP headers from the main Jenkins dashboard using the REST API

        The dashboard headers contain metadata describing the Jenkins instance
        hosting the REST API, including details such as version number, current
        UI theme, and others.

        :rtype: :class:`dict`"""
        if self._jenkins_headers_cache is None:
            temp_path = urllib_parse.urljoin(self.root_url, "api/python")
            req = requests.get(
                temp_path,
                auth=self._creds,
                verify=self._ssl_cert)
            req.raise_for_status()

            self._jenkins_headers_cache = req.headers

        return self._jenkins_headers_cache

    @property
    def jenkins_version(self):
        """Gets the version number of the Jenkins server hosting this REST API

        Typically returns a 3 tuple with the major, minor and update digits of
        the version number

        :rtype: :class:`tuple`"""
        if 'x-jenkins' not in self.jenkins_headers:
            raise InvalidHeader("Jenkins header has no x-jenkins metadata "
                                "attached to it. Can not load version info.")
        return tuple([
            int(i) for i in self.jenkins_headers['x-jenkins'].split(".")
        ])

    def get_api_data(self, target_url=None, query_params=None):
        """retrieves the Jenkins API specific data from the specified URL

        :param str target_url:
            Full URL to the REST API endpoint to be queried. If not provided,
            data will be loaded from the default 'url' for this object
        :param str query_params:
            optional set of query parameters to customize the returned data
        :returns:
            The set of Jenkins attributes, converted to Python objects,
            associated with the given URL.
        :rtype: :class:`dict`
        """
        if target_url is None:
            target_url = self.url

        temp_url = urllib_parse.urljoin(target_url, "api/json")

        if query_params is not None:
            # TODO: Update this to pass 'params' key to get method
            temp_url += "?" + query_params

        req = requests.get(
            temp_url,
            auth=self._creds,
            verify=self._ssl_cert)
        req.raise_for_status()
        retval = req.json()
        self._log.debug(json.dumps(retval, indent=4))
        return retval

    def get_text(self, path=None, params=None):
        """ gets the raw text data from a Jenkins URL

        :param str path:
            optional extension path to append to the root URL managed by this
            object when performing the get operation
        :param dict params:
            optional query parameters to be passed to the request
        :returns: the text loaded from this objects' URL
        :rtype: :class:`str`
        """
        temp_url = self.url
        if path is not None:
            temp_url = urllib_parse.urljoin(temp_url, path.lstrip("/\\"))

        req = requests.get(
            temp_url,
            auth=self._creds,
            verify=self._ssl_cert,
            params=params)
        req.raise_for_status()

        return req.text

    def get_api_xml(self, path=None, params=None):
        """Gets api XML data from a given REST API endpoint

        :param str path:
            optional extension path to append to the root URL managed by this
            object when performing the get operation
        :param dict params:
            optional query parameters to be passed to the request
        :returns: parsed XML data
        """
        temp_url = self.url
        if path is not None:
            temp_url = urllib_parse.urljoin(temp_url, path.lstrip("/\\"))
        temp_url += "/api/xml"
        text = self.get_text(temp_url, params)
        return ElementTree.fromstring(text)

    def post(self, target_url, args=None):
        """sends data to or triggers an operation via a Jenkins URL

        :param str target_url: Full URL to sent post request to
        :param dict args:
            optional set of data arguments to be sent with the post operation.
            Supported keys are as follows:

            * 'headers' - dictionary of HTTP header properties and their
                          associated values
            * 'data' - dictionary of assorted / misc data properties and
                       their values
            * 'files' - dictionary of file names and handles to be uploaded to
                        the target URL
            * 'params' - form data to be passed to the API endpoint
        :returns: reference to the response data returned by the post request
        :rtype: :class:`requests.models.Response`
        """
        if args and "headers" in args:
            temp_headers = args["headers"]
            del args["headers"]
        else:
            temp_headers = dict()

        if self.jenkins_version >= (2, 0, 0) and self.crumb:
            temp_headers.update(self.crumb)

        req = requests.post(
            target_url,
            auth=self._creds,
            verify=self._ssl_cert,
            headers=temp_headers,
            **args if args else dict())

        req.raise_for_status()
        return req

    @property
    def crumb(self):
        """Gets a unique "crumb" identifier required by all POST operations

        Introduced in Jenkins v2

        Output from this helper can be used directly in post operations as an
        HTTP header, something like this:

            requests.post(... headers=self.crumb)

        reference: https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API
        (see CSRF protection section)

        :rtype: :class:`dict`
        """
        if self._crumb_cache is None:
            # Query the REST API for the crumb token
            req = requests.get(
                self.root_url + 'crumbIssuer/api/json',
                auth=self._creds,
                verify=self._ssl_cert)

            if req.status_code == 404:
                # If we get a 404 error, endpoint not found, assume the Cross
                # Site Scripting support has been disabled
                self._crumb_cache = ''
            else:
                req.raise_for_status()
                data = req.json()

                # Seeing as how the crumb for a given Jenkins instance is
                # static, we cache the results locally to prevent having to hit
                # the API unnecessarily
                self._crumb_cache = {
                    data['crumbRequestField']: data['crumb']
                }

        return self._crumb_cache


if __name__ == "__main__":  # pragma: no cover
    pass
