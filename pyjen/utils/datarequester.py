"""Primitives for handling direct IO with the Jenkins REST API"""
import logging
from pyjen.exceptions import JenkinsFlushFailure
import requests
from six.moves import urllib_parse


class DataRequester(object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""

    _text_cache = dict()
    _api_data_cache = dict()
    _header_cache = dict()
    _configxml_cache = dict()
    _needs_flush = False
    # Indicates whether prototype caching logic should be enabled or not
    ENABLE_CACHING = False

    def __init__(self, jenkins_url, ssl_verify=False):
        """
        :param str jenkins_url:
            HTTP URL to use for all subsequent IO operations performed on this object.
        :param bool ssl_verify:
            Indicates whether SSL certificates should be checked when connecting using HTTPS.
        """
        self._url = jenkins_url.rstrip("/\\") + "/"
        self._credentials = None
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
        self._log = logging.getLogger(__name__)

    @property
    def credentials(self):
        """Gets the authentication credentials used for all IO operations on this object

        :returns: user name and password used for authenticated communication with Jenkins
        :rtype: :func:`tuple` of :class:`str`
        """
        return self._credentials

    @credentials.setter
    def credentials(self, creds):
        """Sets new creds for authenticatng this Jenkins connection

        :param tuple creds: 2-tuple containing user name and password
        """
        self._credentials = creds

    @property
    def url(self):
        """Gets the URL used by all IO operations on this object

        :returns: the URL used by all IO operations on this object
        :rtype: :class:`str`
        """
        return self._url

    @property
    def ssl_verify_enabled(self):
        """Checks to see if SSL verification is enabled for REST API transactions or not

        :return: True if transactions are verifying the SSL certificate, False if not
        :rtype: :class:`bool`
        """
        return self._ssl_verify

    def clone(self, new_url=None):
        """create a copy of this connection object

        :param str new_url: optional replacement URL associated with the cloned object
            credentials will be preserved in the clone
        :returns: new DataRequester object, with settings cloned from this instance
        :rtype: :class:`~.datarequester.DataRequester`
        """

        if new_url is not None:
            clone_url = new_url
        else:
            clone_url = self._url

        retval = DataRequester(clone_url, self._ssl_verify)

        if self._credentials:
            retval.credentials = self._credentials

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
        if url in DataRequester._text_cache:
            return DataRequester._text_cache[url]

        self._log.debug("Text cache miss: " + url)

        req = requests.get(url, auth=self._credentials, verify=self._ssl_verify)

        if req.status_code != 200:
            self._log.debug("Error getting raw text from URL: " + url)
            if self._credentials:
                self._log.debug("Authenticating as user: " + self._credentials[0])
                self._log.debug("Details: " + str(req))
            else:
                self._log.debug("Not using authenticated access")

            req.raise_for_status()

        if DataRequester.ENABLE_CACHING:
            DataRequester._text_cache[url] = req.text

        return req.text

    def get_data(self, path=None):
        """Convenience method to convert text data loaded from a Jenkins URL to Python data types

        :param str path:
            optional extension path to append to the root URL managed by this object when performing
            the get operation
        :returns:
            The results of converting the text data loaded from the Jenkins URL into appropriate
            Python objects
        :rtype: :class:`object`
        """
        return eval(self.get_text(path))  # pylint: disable=eval-used

    def get_api_data(self, query_params=None):
        """Convenience method that retrieves the Jenkins API specific data from the specified URL

        :param str query_params: optional set of query parameters to customize the returned data
        :returns:
            The set of Jenkins attributes, converted to Python objects, associated
            with the given URL.
        :rtype: :class:`object`
        """
        cache_url = urllib_parse.urljoin(self._url, "api/python")
        if cache_url in DataRequester._api_data_cache:
            # NOTE: The assumption here is that the query parameters have no impact on the cached data
            # while this may not be true in general, for most use cases intended to be supported this
            # shouldn't be an issue
            return DataRequester._api_data_cache[cache_url]

        temp_url = cache_url
        if query_params is not None:
            temp_url += "?" + query_params

        txt = self._get_raw_text(temp_url)

        retval = eval(txt)  # pylint: disable=eval-used
        if DataRequester.ENABLE_CACHING:
            DataRequester._api_data_cache[cache_url] = retval

        return retval

    def set_api_data(self, cached_api_data):
        """Provides pre-populated Jenkins API data to be cached in the requestor

        This method is typically used by parent objects like views and jobs which batch-load
        data about all of the children objects they contain. This allows the parent to
        pre-populate the data related to their children without having to query the REST API
        for each child.

        :param dict cached_api_data: dictionary of Python objects to be cached in the requestor
        """
        temp_url = urllib_parse.urljoin(self._url, "api/python")
        if DataRequester.ENABLE_CACHING:
            DataRequester._api_data_cache[temp_url] = cached_api_data

    def get_headers(self, path=None):
        """gets the HTTP header attributes from a Jenkins URL

        :param str path:
            optional extension path to append to the root
            URL managed by this object when performing the
            get operation
        :returns: dictionary of HTTP header attributes with their associated values
        :rtype: :class:`dict`
        """

        temp_path = self._url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        if temp_path in DataRequester._header_cache:
            return DataRequester._header_cache[temp_path]

        self._log.debug("Header cache miss: " + temp_path)

        req = requests.get(temp_path, auth=self._credentials)

        if req.status_code != 200:
            req.raise_for_status()

        if DataRequester.ENABLE_CACHING:
            DataRequester._header_cache[temp_path] = req.headers

        return req.headers

    def post(self, path=None, args=None):
        """sends data to or triggers an operation via a Jenkins URL

        :param str path:
            optional extension path to append to the root
            URL managed by this object when performing the
            post operation

        :param dict args:
            optional set of data arguments to be sent with the post operation
            supported keys are as follows:

            * 'headers' - dictionary of HTTP header properties and their associated values
            * 'data' - dictionary of assorted / misc data properties and their values
            * 'files' - dictionary of file names and handles to be uploaded to the target URL
        """

        #TODO: If the cache is currently dirty, flush it
        #TODO: clear the existing cache because posting data of any kind to Jenkins server could potentially
        #      invalidate our cache
        temp_path = self._url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        if args is not None:
            req = requests.post(temp_path, auth=self._credentials, verify=self._ssl_verify, **args)
        else:
            req = requests.post(temp_path, auth=self._credentials, verify=self._ssl_verify)

        if req.status_code != 200:
            self._log.debug("Failed posting Jenkins data to " + temp_path)
            if self._credentials is None:
                self._log.debug("Not using authenticated access")
            else:
                self._log.debug("Authenticating as user: " + self._credentials[0])
            if args is not None:
                self._log.debug("Using custom post data: " + str(args))

            self._log.debug("Details: " + str(req))
            req.raise_for_status()

    @property
    def config_xml(self):
        """Configuration file used to manage the Jenkins entity backed by this object

        :rtype: :class:`str`
        """

        # NOTE: First we check to see whether an entry for this objects config file
        #       exists in the 'modified' configxml cache, and it it does we use it
        #       from there rather than polling the server
        if self._url in DataRequester._configxml_cache:
            self._log.debug("Config.xml read cache hit: " + self._url)
            return DataRequester._configxml_cache[self._url]

        retval = self.get_text("/config.xml")

        return retval

    @config_xml.setter
    def config_xml(self, new_xml):
        """
        :param str new_xml: The new configuration data for this object
        """
        # This is by far the most risky method here
        # The most problematic issue is that here we assume that unique URLs on Jenkins represent unique entities,
        # which is not always the case for example, jobs may exist on multiple views, and can be accessed as
        # sub-components of the view URL, and thus may be accessed
        #       by multiple URLs. If one were to access the same job from different URLs and update the config.xml for
        #       each, this caching mechanism would certainly break down.
        #       Potential Solution: make sure to reduce every URL for every entity to it's shortest form to ensure
        #       consistent URL usage

        #       TODO: Figure out whether this multiplicity problem affects anything other than jobs. It may not.

        # Another potential problem here would be if calls to other methods on this class may invalidate the content of
        # the cached config.xml. For example, maybe if someone renames a job, the cached URL would be invalidated.
        # Maybe there is no way for this to be exploited in practice, but care would need to be taken to ensure this
        # fact
        if DataRequester.ENABLE_CACHING:
            DataRequester._configxml_cache[self._url] = new_xml
            DataRequester._needs_flush = True
        else:
            headers = {'Content-Type': 'text/xml'}
            args = dict()
            args['data'] = new_xml
            args['headers'] = headers
            self.post("/config.xml", args)

    def flush(self):
        """Ensures that any non-synchronized changes cached by this object are uploaded to the remote Jenkins server"""
        self._log.debug("Flushing cached data")
        if not DataRequester._needs_flush:
            self._log.debug("Ignoring clean flush call")
            return

        DataRequester._needs_flush = False

        headers = {'Content-Type': 'text/xml'}

        failed_items = dict()

        for cache_item in DataRequester._configxml_cache:
            args = dict()
            args['data'] = DataRequester._configxml_cache[cache_item]
            args['headers'] = headers
            temp_path = cache_item + "/config.xml"
            req = requests.post(temp_path, auth=self._credentials, **args)
            if req.status_code != 200:
                failed_items[cache_item] = req

        # TODO: After flushing the configxml cache, move those entities over to the textcache for future reference

        if len(failed_items) > 0:
            raise JenkinsFlushFailure(failed_items)

    @staticmethod
    def enable_cache():
        """Enables caching of Jenkins API data

        WARNING: This functionality is in early prototype stage and should not be used in production environments"""
        DataRequester.ENABLE_CACHING = True
        DataRequester.clear()

    def disable_cache(self):
        """Disables caching of Jenkins API data

        WARNING: This functionality is in early prototype stage and should not be used in production environments"""
        DataRequester.ENABLE_CACHING = False
        self.flush()
        DataRequester.clear()

    @property
    def is_dirty(self):
        """Checks to see if there are any unsynchronized changes pending on this object

        :returns: True if there are changes cached in this instance that have not yet been flushed to the remote
                  Jenkins server, False otherwise
        :rtype: :class:`bool`
        """
        return DataRequester._needs_flush

    @classmethod
    def clear(cls):
        """Deletes all cached data so subsequent operations will reload from source

        WARNING: Make sure to call flush() before clear() if there are potentially
        unwritten changes in the cache
        """
        cls._configxml_cache = dict()
        cls._header_cache = dict()
        cls._text_cache = dict()
        cls._api_data_cache = dict()
        cls._needs_flush = False

    def show_debug_info(self):
        """Record some state information in the output logger for debugging purposes"""
        if not DataRequester.ENABLE_CACHING:
            return
        self._log.debug("Destroying datarequester: ")
        self._log.debug("\tText cache size: " + str(len(self._text_cache)))
        self._log.debug("\tAPI data cache size: " + str(len(self._api_data_cache)))
        self._log.debug("\tHeader cache size: " + str(len(self._header_cache)))
        self._log.debug("\tConfig.xml cache size: " + str(len(self._configxml_cache)))
        self._log.debug("\tIs cache dirty?: " + str(self.is_dirty))

if __name__ == "__main__":  # pragma: no cover
    pass
