"""This module contains a set of common helper functions used by one or more
objects in the pyjen package"""
import sys
if sys.version_info.major < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
    
def get_root_url(source_url):
    """Helper function to parse out the root / server URL from an arbitrary URL
    
    Parameter
    ---------
    source_url : string
        Full URL to be parsed, which may contain sub-folders off the main URL,
        such as http://jenkins/view/viewname or http://jenkins/job/jobname.
    
    Returns
    -------
    string
        the root / base portion of the URL of the provided URL
    """
    tmp = urlparse(source_url)
    return tmp.scheme + "://" + tmp.netloc