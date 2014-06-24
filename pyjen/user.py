import urllib
from pyjen.utils.data_requester import data_requester

class user(object):
    """Interface for all primitives for jenkins users
    """
    
    def __init__(self, url, http_io_class=data_requester):
        """Constructor
        
        :param str url: URL of the jenkins user
            
            Examples: 
                * 'http://jenkins/user/JohnSmith'
                
        :param obj http_io_class:
            class capable of handling HTTP IO requests between
            this class and the Jenkins REST API
            If not explicitly defined a standard IO class will be used 
        """
        self._requester = http_io_class(url)
        self._url = url
        self._description = ""
        self._fullName = ""
        self._id = ""
        self._emailAddress = ""
        
        self._requester = data_requester(url)
           
        data = self._requester.get_api_data()      
        
        # Set all private class members
        self._description = data['description'] 
        self._fullName = data["fullName"]
        self._id = data["id"]
                        
        for property in data["property"]:    
            if ("address" in property.keys()):
                self._emailAddress = property["address"]                 
            
        
        
        
    @property
    def email(self):
        return self._emailAddress
    
    @property
    def id(self):
        return self._id
    
    @property
    def fullName(self):
        return self._fullName
    
    @property 
    def description(self):
        return self._description        
    
    
if __name__ == "__main__":
    test = user("http://builds.caris.priv/user/jdyer")   
    print(test.email) 
    
        