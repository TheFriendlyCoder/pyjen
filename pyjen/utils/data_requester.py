import requests

class data_requester (object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""
    
    def __init__ (self, url, user, password):
        """constructor
        
        Parameters
        ----------
        url : string
            root URL of the REST API to be accessed for subsequent IO operations
        user : string
            user name to authenticate with the API
            May be set to None for unauthenticated access
        password : string
            password for the specified user credentials
            If a user name is provided this parameter must be non empty
        """
        
        self.__url = url
        self.__user = user
        self.__password = password
        
        #If the caller provides a user name they must provide a password
        if self.__user != None:
            assert(self.__password != None)
    
    def get_user(self):
        """ gets the user name used to authenticate to this HTTP request object
        
        Returns
        -------
        string
            user name used to authenticate transactions made through this object
            may be 'none'
        """
        return self.__user
    
    def get_password(self):
        """ gets the password used to authenticate to this HTTP request object
        
        Returns
        -------
        string
            password used to authenticate transactions made through this object
            may be 'none'
        """
        return self.__password
    
    def get_text(self, sub_url=None):
        """ gets the raw text data from the URL associated with this object
        
        Parameter
        ---------
        url : string
            optional sub-folder to append to the root API URL to use
            when processing this request.
            If not defined the root URL (as provided to the constructor)
            will be used directly
            
        Return
        ------
        string
            the text loaded from this objects' URL
        """
            
        temp_url = self.__url
        if sub_url != None:
            temp_url = temp_url + sub_url
            
        if self.__user != None:
            r = requests.get(temp_url, auth=(self.__user, self.__password))
        else:
            r = requests.get(temp_url)
        
        if r.status_code != 200:
            r.raise_for_status()
        
        return r.text
        
    def get_data(self, sub_url=None):
        """shorthand helper that converts the text data loaded from the objects' URL to Python data types
        
        Parameter
        ---------
        sub_url : string
            optional sub-folder to append to the root API URL to use
            when processing this request.
            If not defined the root URL (as provided to the constructor)
            will be used directly

        Return
        ------
        object
            The results of converting the text data loaded from the objects' 
            URL into appropriate Python objects
        """
        return eval(self.get_text(sub_url))
    
    def get_headers(self, sub_url=None):
        """gets the HTTP header attributes from the URL managed by this object
        
        Parameter
        ---------
        sub_url : string
            optional sub-folder to append to the root API URL to use
            when processing this request.
            If not defined the root URL (as provided to the constructor)
            will be used directly

        Return
        ------
        dictionary
            dictionary of HTTP header attributes with their associated values
        """
        
        temp_url = self.__url
        if sub_url != None:
            temp_url = temp_url + sub_url
            
        if self.__user != None:
            r = requests.get(temp_url, auth=(self.__user, self.__password))
        else:
            r = requests.get(temp_url)
            
        if r.status_code != 200:
            r.raise_for_status()
            
        return r.headers
    
    def post(self, sub_url=None, args=None):
        """sends a post operation to the URL managed by this object
        
        Parameters
        ----------
        sub_url : string
            optional sub-folder to append to the root API URL to use
            when processing this request.
            If not defined the root URL (as provided to the constructor)
            will be used directly

        args : dictionary
            optional set of data arguments to be sent with the post operation
            supported keys are as follows:
            
            * 'headers' - dictionary of HTTP header properties and their associated values
            * 'data' - dictionary of assorted / misc data properties and their values 
        """
        temp_url = self.__url
            
        if sub_url != None:
            temp_url = temp_url + sub_url
            
        if args != None:
            if self.__user != None:
                r = requests.post(temp_url, auth=(self.__user, self.__password), **args)
            else:
                r = requests.post(temp_url, **args)
        else:
            if self.__user != None:
                r = requests.post(temp_url, auth=(self.__user, self.__password))
            else:
                r = requests.post(temp_url)

        if r.status_code != 200:
            r.raise_for_status()
            
    def post_url(self, full_url, args = None):
        """ posts data to an absolute URL instead of the default URL provided to this object upon creation
        
        Parameters
        ----------
        full_url : string
            the full HTTP address to post the data to 
        args : dictionary
            optional set of data arguments to be sent with the post operation
            supported keys are as follows:
            
            * 'headers' - dictionary of HTTP header properties and their associated values
            * 'data' - dictionary of assorted / misc data properties and their values 
        """
        if args != None:
            r = requests.post(full_url, **args)
        else:
            r = requests.post(full_url)
        
        if r.status_code != 200:
            r.raise_for_status()