import time
import urllib
from pyjen.utils.data_requester import data_requester

class node(object):
    """Wrapper around a Jenkins build agent (aka: node) configuration
    
    Use this class to manipulate agents managed by a Jenkins master"""
    
    def __init__(self, url, user=None, password=None):
        """Constructor
        
        Parameters
        ----------
        url : string
            root URL of the node being managed by this object
            Example: 'http://jenkins/computer/mynode/'
        user : string
            optional user name to authenticate to Jenkins dashboard
        password : string
            password for Jenkins login credentials 
            if a user name is provided this parameter must be defined as well
        """
        if (user != None):
            assert (password != None)

        self.__url = url
        self.__requester = data_requester(url, user, password)
        
    def get_url(self):
        """Returns the root URL of the REST API used to manage this node"""
        return self.__url
    
    def get_name(self):
        """Gets the display name of this node
        
        Return
        ------
        string
            the name of this node
        """        
        data = self.__requester.get('/api/python')
        
        return data['displayName']
    
    def is_offline(self):
        """Checks to see whether this node is currently offline or not
        
        Return
        ------
        boolean
            true if this node is offline otherwise false
        """
        data = self.__requester.get('/api/python')
        
        return data['offline']
    
    def toggle_offline(self, message=None):
        """Toggles the online status of this node
        
        If the current state of this node is "offline" it will
        be toggled to "online" when calling this method, and vice
        versa.
        
        Parameter
        ---------
        message : text
            optional descriptive message to display on the dashboard explaining
            the reason for this operation.
        """
        #TODO: See if I can rework this to use args properties
        if message != None:
            post_cmd = "/toggleOffline?offlineMessage=" + urllib.quote(message)
        else:
            post_cmd = "/toggleOffline"
            
        self.__requester.post(post_cmd)
        
    def is_idle(self):
        """Checks to see whether any executors are in use on this node or not
        
        Return
        ------
        boolean
            returns true if there are no active builds on this node at the moment
            otherwise returns false
        """
        data = self.__requester.get_data('/api/python')
        
        return data['idle']
    
    def wait_for_idle(self, max_timeout=None):
        """Blocks execution until this node enters an idle state
        
        Parameters
        ----------
        max_timeout : integer
            The maximum amount of time, in seconds, to wait for
            an idle state. If this value is undefined, this method
            will block indefinitely.
                
        Returns
        -------
        boolean
            true if the node has entered idle state before returning
            otherwise returns false
        """
        if max_timeout != None:
            while not self.is_idle():
                time.sleep(5)
        else:
            total_wait_time = 0
            while not self.is_idle():
                time.sleep(5)
                total_wait_time += 5
                if total_wait_time >= max_timeout:
                    break
            
        return self.is_idle()