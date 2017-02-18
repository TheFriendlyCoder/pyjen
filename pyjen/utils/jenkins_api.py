"""Base class for all objects that interact directly with the Jenkins REST API"""
import logging
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

    def __init__(self, url):
        self._url = url.rstrip("/\\") + "/"

        # NOTE: Here we configure a private logging object, which should sufficiently obfuscate the member
        #       so derived classes can have their own logging interface.
        self.__log = logging.getLogger(__name__)

    @property
    def url(self):
        """Gets the URL for the REST API endpoint used by this object"""
        return self._url

    def get_api_data(self, query_params=None):
        """Convenience method that retrieves the Jenkins API specific data from the specified URL

        :param str query_params: optional set of query parameters to customize the returned data
        :returns:
            The set of Jenkins attributes, converted to Python objects, associated
            with the given URL.
        :rtype: :class:`object`
        """
        temp_url = urllib_parse.urljoin(self._url, "api/json")

        if query_params is not None:
            temp_url += "?" + query_params

        return self._get_with_check(temp_url).json()

    def get_text(self, path=None):
        """ gets the raw text data from a Jenkins URL

        :param str path: optional extension path to append to the root URL managed by this object
            when performing the get operation

        :returns: the text loaded from this objects' URL
        :rtype: :class:`str`
        """
        tmp = self._url
        if path is not None:
            tmp = urllib_parse.urljoin(tmp, path.lstrip("/\\"))

        return self._get_with_check(tmp).text

    def _get_with_check(self, url):
        """retrieves the raw text output from a specified HTTP URL

        :param str url: the full HTTP URL to be polled
        :returns:  Text returned from the given URL
        :rtype: :class:`str`
        """
        req = requests.get(url, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled)

        if req.status_code != requests.codes.ok:
            self.__log.debug("Error getting raw text from URL: " + url)
            if JenkinsAPI.creds:
                self.__log.debug("Authenticating as user: " + JenkinsAPI.creds[0])
                self.__log.debug("Details: " + str(req))
            else:
                self.__log.debug("Not using authenticated access")

            req.raise_for_status()

        return req

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

        temp_path = self._url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        if args is not None:
            req = requests.post(temp_path, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled, **args)
        else:
            req = requests.post(temp_path, auth=JenkinsAPI.creds, verify=JenkinsAPI.ssl_verify_enabled)

        if req.status_code != requests.codes.ok:
            self.__log.debug("Failed posting Jenkins data to " + temp_path)
            if JenkinsAPI.creds:
                self.__log.debug("Authenticating as user: " + JenkinsAPI.creds[0])
            else:
                self.__log.debug("Not using authenticated access")

            if args is not None:
                self.__log.debug("Using custom post data: " + str(args))

            self.__log.debug("Details: " + str(req))
            req.raise_for_status()
