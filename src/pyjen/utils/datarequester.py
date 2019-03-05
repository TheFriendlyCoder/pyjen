"""Primitives for handling direct IO with the Jenkins REST API"""
import logging
import requests
from six.moves import urllib_parse


class DataRequester(object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""

    def __init__(self, jenkins_url, ssl_verify=False):
        """
        :param str jenkins_url:
            HTTP URL to use for all subsequent IO operations performed on
            this object.
        :param bool ssl_verify:
            Indicates whether SSL certificates should be checked when
            connecting using HTTPS.
        """
        self._url = jenkins_url.rstrip("/\\") + "/"
        self._credentials = None
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
        self._log = logging.getLogger(__name__)

    @property
    def credentials(self):
        """authentication credentials used for all IO operations on this object

        :returns:
            user name and password used for authenticated communication with
            Jenkins
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
        """see if SSL verification is enabled for REST API transactions or not

        :return:
            True if transactions are verifying the SSL certificate, False if not
        :rtype: :class:`bool`
        """
        return self._ssl_verify

    def clone(self, new_url=None):
        """create a copy of this connection object

        :param str new_url:
            optional replacement URL associated with the cloned object
            credentials will be preserved in the clone
        :returns:
            new DataRequester object, with settings cloned from this instance
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

        :param str path:
            optional extension path to append to the root URL managed by this
            object when performing the get operation

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
        req = requests.get(url, auth=self._credentials, verify=self._ssl_verify)

        if req.status_code != 200:
            self._log.debug("Error getting raw text from URL: %s", url)
            if self._credentials:
                self._log.debug("Authenticating as user: %s",
                                self._credentials[0])
                self._log.debug("Details: %s", str(req))
            else:
                self._log.debug("Not using authenticated access")

            req.raise_for_status()

        return req.text

    def get_data(self, path=None):
        """converts text data loaded from a Jenkins URL to Python data types

        :param str path:
            optional extension path to append to the root URL managed by this
            object when performing the get operation
        :returns:
            The results of converting the text data loaded from the Jenkins URL
            into appropriate Python objects
        :rtype: :class:`object`
        """
        return eval(self.get_text(path))  # pylint: disable=eval-used

    def get_api_data(self, query_params=None):
        """retrieves the Jenkins API specific data from the specified URL

        :param str query_params:
            optional set of query parameters to customize the returned data
        :returns:
            The set of Jenkins attributes, converted to Python objects,
            associated with the given URL.
        :rtype: :class:`object`
        """
        temp_url = urllib_parse.urljoin(self._url, "api/python")

        if query_params is not None:
            temp_url += "?" + query_params

        txt = self._get_raw_text(temp_url)

        retval = eval(txt)  # pylint: disable=eval-used

        return retval

    def get_headers(self, path=None):
        """gets the HTTP header attributes from a Jenkins URL

        :param str path:
            optional extension path to append to the root
            URL managed by this object when performing the
            get operation
        :returns:
            dictionary of HTTP header attributes with their associated values
        :rtype: :class:`dict`
        """

        temp_path = self._url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        req = requests.get(temp_path, auth=self._credentials)

        if req.status_code != 200:
            req.raise_for_status()

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

            * 'headers' - dictionary of HTTP header properties and their
                          associated values
            * 'data' - dictionary of assorted / misc data properties and their
                       values
            * 'files' - dictionary of file names and handles to be uploaded to
                        the target URL
        """
        temp_path = self._url
        if path is not None:
            temp_path = urllib_parse.urljoin(temp_path, path.lstrip("/\\"))

        if args is not None:
            req = requests.post(
                temp_path,
                auth=self._credentials,
                verify=self._ssl_verify,
                **args)
        else:
            req = requests.post(
                temp_path, auth=self._credentials, verify=self._ssl_verify)

        if req.status_code != 200:
            self._log.debug("Failed posting Jenkins data to %s", temp_path)
            if self._credentials is None:
                self._log.debug("Not using authenticated access")
            else:
                self._log.debug("Authenticating as user: %s",
                                self._credentials[0])
            if args is not None:
                self._log.debug("Using custom post data: %s", str(args))

            self._log.debug("Details: %s", req)
            req.raise_for_status()

    @property
    def config_xml(self):
        """Configuration used to manage the Jenkins entity backed by this object

        :rtype: :class:`str`
        """
        retval = self.get_text("/config.xml")

        return retval

    @config_xml.setter
    def config_xml(self, new_xml):
        """
        :param str new_xml: The new configuration data for this object
        """
        headers = {'Content-Type': 'text/xml'}
        args = dict()
        args['data'] = new_xml
        args['headers'] = headers
        self.post("/config.xml", args)


if __name__ == "__main__":  # pragma: no cover
    pass
