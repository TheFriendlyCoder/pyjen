"""Primitives for handling direct IO with the Jenkins REST API"""
import requests
import sys
if sys.version_info.major < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin


class DataRequester (object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""    
        
    def __init__(self, jenkins_url, username, password):
        """Constructor
        
        :param str jenkins_url: 
            HTTP URL to use for all subsequent IO operations performed on this object.
        :param str username:
            Jenkins user name to use for authentication. May be set to None for anonymous access.
        :param str password:
            Password for the given Jenkins user, to use for authentication. May be set to None
            for anonymous access.
        """

        self._url = jenkins_url.rstrip("/\\") + "/"
        if not username or not password:
            self._credentials = None
        else:
            self._credentials = (username, password)
        
    @property
    def url(self):
        """Gets the URL used by all IO operations on this object"""
        return self._url
    
    @property
    def credentials(self):
        """Gets the authentication credentials used for all IO operations on this object"""
        return self._credentials
    
    def clone(self, new_url=None):
        """create a copy of this connection object
        
        :param str new_url: optional replacement URL associated with the cloned object
            credentials will be preserved in the clone
        :returns: new :py:class:`DataRequester` object, with settings cloned from this instance
        :rtype: :py:class:`DataRequester`
        """
        
        if new_url is not None:
            clone_url = new_url
        else:
            clone_url = self._url

        if self._credentials:
            return DataRequester (clone_url, self._credentials[0], self._credentials[1])
        else:
            return DataRequester (clone_url, None, None)
        
    def get_text(self, path=None):
        """ gets the raw text data from a Jenkins URL

        :param str path: optional extension path to append to the root URL managed by this object 
            when performing the get operation
            
        :returns: the text loaded from this objects' URL
        :rtype: :func:`str`
        
        """
        tmp = self._url
        if path is not None:
            tmp = urljoin(tmp, path.lstrip("/\\"))  
        
        return self._get_raw_text(tmp)
    
    def _get_raw_text(self, url):
        """retrieves the raw text output from a specified HTTP URL
        
        :param str url: the full HTTP URL to be polled
        :returns:  Text returned from the given URL
        :rtype: :func:`str`
        """
        req = requests.get(url, auth=self._credentials)
        
        if req.status_code != 200:
            req.raise_for_status()
        
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
        return eval(self.get_text(path))
    
    def get_api_data(self):
        """Convenience method that retrieves the Jenkins API specific data from the specified URL
        
        :returns:
            The set of Jenkins attributes, converted to Python objects, associated
            with the given URL.
        :rtype: :class:`object`
        """
        temp_url = urljoin(self._url, "api/python")
        
        txt = self._get_raw_text(temp_url)
        
        return eval(txt)
    
    def get_headers(self, path=None):
        """gets the HTTP header attributes from a Jenkins URL
        
        :param str path:
            optional extension path to append to the root
            URL managed by this object when performing the
            get operation
        :returns: dictionary of HTTP header attributes with their associated values
        :rtype: :func:`dict`
        """
        
        temp_path = self._url
        if path is not None:
            temp_path = urljoin(temp_path, path.lstrip("/\\"))    
        
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
            
            * 'headers' - dictionary of HTTP header properties and their associated values
            * 'data' - dictionary of assorted / misc data properties and their values 
        """          
        temp_path = self._url
        if path is not None:
            temp_path = urljoin(temp_path, path.lstrip("/\\"))
              
        if args is not None:
            req = requests.post(temp_path, auth=self._credentials, **args)
        else:
            req = requests.post(temp_path, auth=self._credentials)

        if req.status_code != 200:
            req.raise_for_status()
            
if __name__ == "__main__":  # pragma: no cover
    pass
