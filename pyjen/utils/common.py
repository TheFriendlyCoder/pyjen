"""This module contains a set of common helper functions used by one or more
objects in the pyjen package"""
import sys
if sys.version_info.major < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse
    
#todo: deprecate this function since it should never be used. callers can use the global properties object now
def get_root_url(source_url):
    """Helper function to parse out the root / server URL from an arbitrary URL
    
    :param str source_url:
        Full URL to be parsed, which may contain sub-folders off the main URL,
        such as http://jenkins/view/viewname or http://jenkins/job/jobname.
    :returns: the root / base portion of the URL of the provided URL
    :rtype: :func:`str`
    """
    tmp = urlparse(source_url)
    return tmp.scheme + "://" + tmp.netloc