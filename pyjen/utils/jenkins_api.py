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
    def __init__(self, url, credentials, ssl_verify):
        self._url = url.rstrip("/\\") + "/"
        self._creds = credentials
        self._ssl_verify = ssl_verify

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
        temp_url = urllib_parse.urljoin(self._url, "api/python")

        if query_params is not None:
            temp_url += "?" + query_params

        txt = self._get_raw_text(temp_url)

        retval = eval(txt)  # pylint: disable=eval-used
        return retval

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

        return self._get_raw_text(tmp)

    def _get_raw_text(self, url):
        """retrieves the raw text output from a specified HTTP URL

        :param str url: the full HTTP URL to be polled
        :returns:  Text returned from the given URL
        :rtype: :class:`str`
        """
        req = requests.get(url, auth=self._creds, verify=self._ssl_verify)

        if req.status_code != 200:
            self.__log.debug("Error getting raw text from URL: " + url)
            if self._creds is None:
                self.__log.debug("Not using authenticated access")
            else:
                self.__log.debug("Authenticating as user: " + self._creds[0])
                self.__log.debug("Details: " + str(req))
            req.raise_for_status()

        return req.text
