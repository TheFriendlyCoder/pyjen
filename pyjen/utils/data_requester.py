import requests
import sys
from pyjen.user_params import GlobalParams
if sys.version_info.major < 3:
    from urlparse import urljoin, urlparse
else:
    from urllib.parse import urljoin, urlparse

class data_requester (object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""    
        
    def __init__(self, url=None):
        """Constructor
        
        :param str url: Optional source URL to use for all subsequent IO operations performed on this object. May be partial path, relative to the Jenkins root URL, or a full standalone URL.
        
        If not defined, all operations will be directed at the
        root Jenkins URL.
        
        NOTE: As a convenience, full URLs with the same root path
        as that provided by the GlobalParams object are acceptable
        inputs.
        
        """
        self.__base_url = GlobalParams().jenkins_url.rstrip("/") + "/"
        if (url == None):
            return
        
        parsed_url = urlparse(url)
        if (parsed_url.scheme != ""):
            #if input URL has a connection scheme (e.g. 'http') prefix,
            #assume it is a full URL and use it explicitly here
            self.__base_url = url.rstrip("/") + "/"
        else:
            #the urlparse library does some weird things when there are
            #superfluous leading or trailing / characters in any of the
            #paths, so we need to take care to trim any such characters off
            tmp_url = GlobalParams().jenkins_url
            tmp_url = tmp_url.rstrip("/")
            tmp_url += "/"
            tmp_url = urljoin(tmp_url, url.lstrip("/").rstrip("/"))
            self.__base_url = tmp_url + "/"
            
    def get_text(self, path=None):
        """ gets the raw text data from a Jenkins URL

        :param str path: optional extension path to append to the root URL managed by this object when performing the get operation
            
        :returns: the text loaded from this objects' URL
        :rtype: :func:`str`
        
        """
            
        return self._get_raw_text(urljoin(self.url, path.lstrip("/")))
    
    def _get_raw_text(self, url):
        """retrieves the raw text output from a specified HTTP URL
        
        :param str url: the full HTTP URL to be polled
        :returns:  Text returned from the given URL
        :rtype: :func:`str`
        """
        r = requests.get(url, auth=GlobalParams().credentials)
        
        if r.status_code != 200:
            r.raise_for_status()
        
        return r.text
        
    def get_data(self, path=None):
        """Convenience method that converts the text data loaded from a Jenkins URL to Python data types
        
        :param str path:
            optional extension path to append to the root
            URL managed by this object when performing the
            get operation
            
        :returns:
            The results of converting the text data loaded from the Jenkins 
            URL into appropriate Python objects
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
        temp_url = urljoin(self.url, "api/python")
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
            
        r = requests.get(urljoin(self.url, path.lstrip("/")), auth=GlobalParams().credentials)
            
        if r.status_code != 200:
            r.raise_for_status()
            
        return r.headers
    
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
        if args != None:
            r = requests.post(urljoin(self.url, path.lstrip("/")), auth=GlobalParams().credentials, **args)
        else:
            r = requests.post(urljoin(self.url, path.lstrip("/")), auth=GlobalParams().credentials)

        if r.status_code != 200:
            r.raise_for_status()
            


    @property
    def url(self):
        """Gets the root URL used for IO operations by this object
        
        NOTE: This root URL will always have a trailing '/' character
        to simplify other processes
        
        :returns: root URL used for IO operations by this object
        :rtype: :func:`str`
        """
        return self.__base_url
            
#import urllib.parse 
if __name__ == "__main__":
    pass