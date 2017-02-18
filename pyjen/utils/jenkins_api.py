"""Base class for all objects that interact directly with the Jenkins REST API"""
import requests
from six.moves import urllib_parse


class JenkinsAPI(object):
    """Base class for all objects that interact with the Jenkins REST API

    This class provides methods for interacting with the Jenkins REST API in various ways such as querying
    a specific API endpoint for data or posting new data to a listening endpoint. Classes requiring this
    functionality should simply derive from this base class so they can make calls directly to the helpers,
    while the base class maintains the connection parameters and state information for optimizing IO against
    the remote Jenkins service."""

    # Credentials to use when authenticating to the Jenkins REST API
    creds = ()

    # Indicates whether SSL encryption certificates should be verified when connecting to secure servers
    # Can cause connection problems when enabled if Jenkins is using a self-signed SSL certificate
    ssl_verify_enabled = False

    # Static data member intended to cache the Jenkins REST API 'crumb' token for use with POST operations
    # typically populated by the 'crumb' property method upon first execution
    crumb_cache = None

    # Generated static member containing the root URL for the currently selected Jenkins instance
    # Typically will be populated by the 'root_url' property method, but may be overloaded directly
    # if your Jenkins instance has an obfuscated URL (ie: http://someserver/jenkins/ say)
    # The member can be overloaded as follows:
    #       JenkinsAPI.jenkins_root_url = "http://someserver/jenkins/"
    jenkins_root_url = None

    # Static member intended to cache the header information provided by the main dashboard URL
    # This header information is static and never changes for any given session so we cache it here
    # to minimize the times we need to query the REST API
    jenkins_headers_cache = None

    def __init__(self, url):
        self._url = url.rstrip("/\\") + "/"

    @property
    def url(self):
        """Gets the URL for the REST API endpoint used by this object

        NOTE: The URL returned by this property is guaranteed to end with a trailing slash character

        :rtype: :class:`str`"""
        return self._url

    @property
    def root_url(self):
        """Gets the root URL pointing to the main Jenkins dashboard associated with the current object

        NOTE: This property assumes that the main Jenkins dashboard is available under the root domain
        of the host it is running on, which would use URLs of the following form:
            http(s)://servername[:port#]/

        If the host running Jenkins sits behind a proxy or some other HTTP redirection service, you will
        need to manually override the JenkinsAPI.jenkins_root_url property

        NOTE: The URL returned by this property is guaranteed to end with a trailing slash character

        :rtype: :class:`str`
        """
        if JenkinsAPI.jenkins_root_url is None:
            url_parts = urllib_parse.urlparse(self.url)
            JenkinsAPI.jenkins_root_url = url_parts.scheme + "://" + url_parts.netloc + "/"

        # Sanity check: make sure our root URL ends with a slash character. This check should only potentially
        #               fail if someone overloads the data member directly and sets it incorrectly
        assert JenkinsAPI.jenkins_root_url[-1] == "/"

        return JenkinsAPI.jenkins_root_url

    @property
    def jenkins_headers(self):
        """Gets the HTTP headers from the main Jenkins dashboard using the REST API

        The dashboard headers contain metadata describing the Jenkins instance hosting the REST API, including
        details such as version number, current UI theme, and others.

        :rtype: :class:`dict`"""
        if JenkinsAPI.jenkins_headers_cache is None:
            temp_path = urllib_parse.urljoin(self.root_url, "api/python")
            req = requests.get(temp_path, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled)
            req.raise_for_status()

            JenkinsAPI.jenkins_headers_cache = req.headers

        return JenkinsAPI.jenkins_headers_cache

    @property
    def jenkins_version(self):
        """Gets the version number of the Jenkins server hosting this REST API

        Typically returns a 3 tuple with the major, minor and update digits of the version number

        :rtype: :class:`tuple`"""
        if 'x-jenkins' not in self.jenkins_headers:
            raise ConnectionError("Jenkins header has no x-jenkins metadata attached to it. Can not load version info.")

        return tuple([int(i) for i in self.jenkins_headers['x-jenkins'].split(".")])

    def get_api_data(self, query_params=None):
        """Convenience method that retrieves the Jenkins API specific data from the specified URL

        :param str query_params: optional set of query parameters to customize the returned data
        :returns:
            The set of Jenkins attributes, converted to Python objects, associated
            with the given URL.
        :rtype: :class:`object`
        """
        temp_url = urllib_parse.urljoin(self.url, "api/json")

        if query_params is not None:
            temp_url += "?" + query_params

        req = requests.get(temp_url, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled)
        req.raise_for_status()
        return req.json()

    def get_text(self, path=None):
        """ gets the raw text data from a Jenkins URL

        :param str path: optional extension path to append to the root URL managed by this object
            when performing the get operation

        :returns: the text loaded from this objects' URL
        :rtype: :class:`str`
        """
        temp_url = self.url
        if path is not None:
            temp_url = urllib_parse.urljoin(temp_url, path.lstrip("/\\"))

        req = requests.get(temp_url, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled)
        req.raise_for_status()

        return req.text

    def post(self, path=None, args=None):
        """sends data to or triggers an operation via a Jenkins URL

        :param str path:
            optional extension path to append to the root URL managed by this object when performing the post operation

        :param dict args:
            optional set of data arguments to be sent with the post operation.  Supported keys are as follows:

            * 'headers' - dictionary of HTTP header properties and their associated values
            * 'data' - dictionary of assorted / misc data properties and their values
            * 'files' - dictionary of file names and handles to be uploaded to the target URL
        """

        temp_path = self.url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        temp_headers = dict()
        if self.jenkins_version >= (2, 0, 0):
            temp_headers.update(self.crumb)

        req = requests.post(
            temp_path,
            auth=JenkinsAPI.creds,
            verify=JenkinsAPI.ssl_verify_enabled,
            headers=temp_headers,
            **args if args else dict())

        req.raise_for_status()

    @property
    def crumb(self):
        """Gets a unique "crumb" identifier required by all POST operations supported by Jenkins 2

        Output from this helper can be used directly in post operations as an HTTP header, something like this:

            requests.post(... headers=self.crumb)

        reference: https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API (see CSRF protection section)

        :rtype: :class:`dict`
        """
        if JenkinsAPI.crumb_cache is None:
            # Query the REST API for the crumb token
            req = requests.get(
                self.root_url + 'crumbIssuer/api/json',
                auth=JenkinsAPI.creds,
                verify=JenkinsAPI.ssl_verify_enabled)
            req.raise_for_status()
            data = req.json()

            # Seeing as how the crumb for a given Jenkins instance is static, we cache the results locally
            # to prevent having to hit the API unnecessarily
            JenkinsAPI.crumb_cache = {data['crumbRequestField']: data['crumb']}

        return JenkinsAPI.crumb_cache


if __name__ == "__main__":
    pass
