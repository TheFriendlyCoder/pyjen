"""Base class for all objects that interact with the Jenkins REST API"""
from urllib.parse import urljoin
import logging
import json
from xml.etree import ElementTree
from requests.exceptions import InvalidHeader


class JenkinsAPI:
    """Abstraction around the raw Jenkins REST API"""

    def __init__(self, url, session):
        """
        Args:
            url (str):
                URL of the Jenkins API endpoint to manage
            session (requests.Session):
                HTTP session to use for interacting with the Jenkins REST API
        """
        self._log = logging.getLogger(__name__)
        self._session = session

        self._url = url.rstrip("/\\") + "/"
        self._jenkins_root_url = self._url

        # Internal data members used for caching certain API response data
        # to improve performance
        self._crumb_cache = None
        self._jenkins_headers_cache = None

    def __str__(self):
        return self.url

    def __repr__(self):
        return f"({type(self)}: {self.url})"

    def clone(self, api_url):
        """Creates a copy of this instance, for a new endpoint URL

        Args:
            api_url (str):
                URL for the new REST API endpoint to be managed

        Returns:
            JenkinsAPI:
                reference to the newly created API interface
        """
        retval = JenkinsAPI(api_url, self._session)
        retval._jenkins_root_url = self._jenkins_root_url  # pylint: disable=protected-access
        return retval

    @property
    def url(self):
        """str: the URL for the REST API endpoint managed by this object

        NOTE: The URL returned by this property is guaranteed to end with a
        trailing slash character
        """
        return self._url

    @property
    def root_url(self):
        """str: URL of the main Jenkins dashboard associated with the current
        object

        NOTE: The URL returned by this property is guaranteed to end with a
        trailing slash character
        """
        return self._jenkins_root_url

    @property
    def jenkins_headers(self):
        """dict: HTTP headers from the main Jenkins dashboard using the REST API

        The dashboard headers contain metadata describing the Jenkins instance
        hosting the REST API, including details such as version number, current
        UI theme, and others.
        """
        if self._jenkins_headers_cache is None:
            temp_path = urljoin(self.root_url, "api/python")
            req = self._session.get(temp_path)
            req.raise_for_status()

            self._jenkins_headers_cache = req.headers

        return self._jenkins_headers_cache

    @property
    def jenkins_version(self):
        """tuple: version number of the Jenkins server hosting this REST API,
        parsed into a tuple of integers

        Typically returns a 3 tuple with the major, minor and update digits of
        the version number
        """
        if 'x-jenkins' not in self.jenkins_headers:
            raise InvalidHeader("Jenkins header has no x-jenkins metadata "
                                "attached to it. Can not load version info.")
        return tuple(
            int(i) for i in self.jenkins_headers['x-jenkins'].split(".")
        )

    def get_api_data(self, target_url=None, query_params=None):
        """retrieves the Jenkins API specific data from the specified URL

        Args:
            target_url (str):
                Full URL to the REST API endpoint to be queried. If not
                provided, data will be loaded from the default 'url' for this
                object
            query_params (str):
                optional set of query parameters to customize the returned data

        Returns:
            dict:
                The set of Jenkins attributes, converted to Python objects,
                associated with the given URL.
        """
        if target_url is None:
            target_url = self.url

        temp_url = urljoin(target_url, "api/json")

        if query_params is not None:
            # TODO: Update this to pass 'params' key to get method
            temp_url += "?" + query_params

        req = self._session.get(temp_url)
        req.raise_for_status()
        retval = req.json()
        self._log.debug(json.dumps(retval, indent=4))
        return retval

    def get_text(self, path=None, params=None):
        """ gets the raw text data from a Jenkins URL

        Args:
            path (str):
                optional extension path to append to the root URL managed by
                this object when performing the get operation
            params (dict):
                optional query parameters to be passed to the request

        Returns:
            str:
                the text loaded from this objects' URL
        """
        temp_url = self.url
        if path is not None:
            temp_url = urljoin(temp_url, path.lstrip("/\\"))

        req = self._session.get(temp_url, params=params)
        req.raise_for_status()

        return req.text

    def get_api_xml(self, path=None, params=None):
        """Gets api XML data from a given REST API endpoint

        Args:
            path (str):
                optional extension path to append to the root URL managed by
                this object when performing the get operation
            params (dict):
                optional query parameters to be passed to the request

        Returns:
            xml.etree.ElementTree.Element:
                parsed XML data
        """
        temp_url = self.url
        if path is not None:
            temp_url = urljoin(temp_url, path.lstrip("/\\"))
        temp_url += "/api/xml"
        text = self.get_text(temp_url, params)
        return ElementTree.fromstring(text)

    def post(self, target_url, args=None):
        """sends data to or triggers an operation via a Jenkins URL

        Args:
            target_url (str):
                Full URL to sent post request to
            args (dict):
                optional set of data arguments to be sent with the post
                operation.

        Returns:
            requests.Response:
                reference to the response data returned by the post request
        """
        if args and "headers" in args:
            temp_headers = args["headers"]
            del args["headers"]
        else:
            temp_headers = {}

        if self.jenkins_version >= (2, 0, 0) and self.crumb:
            temp_headers.update(self.crumb)

        req = self._session.post(
            target_url,
            headers=temp_headers,
            **args if args else {})

        req.raise_for_status()
        return req

    @property
    def crumb(self):
        """dict: unique "crumb" identifier required by all POST operations

        Introduced in Jenkins v2

        Output from this helper can be used directly in post operations as an
        HTTP header, something like this:

        ::

            requests.post(... headers=self.crumb)

        reference: https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API
        (see CSRF protection section)
        """
        if self._crumb_cache is None:
            # Query the REST API for the crumb token
            req = self._session.get(self.root_url + 'crumbIssuer/api/json')

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
