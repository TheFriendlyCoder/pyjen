import requests

class data_requester (object):
    """Abstraction layer encapsulate all IO requests for the Jenkins REST API"""
    
    def __init__ (self, url, user, password):
        self.__url = url
        self.__user = user
        self.__password = password
        
        #If the caller provides a user name they must provide a password
        if self.__user != None:
            assert(self.__password != None)
    
    def get_text(self):
        if self.__user != None:
            r = requests.get(self.__url, auth=(self.__user, self.__password))
        else:
            r = requests.get(self.__url)
        
        #todo: improve error detection and reporting (e.g.: if authentication failed, provide an appropriate notification)    
        assert(r.status_code == 200)
        
        return r.text
        
    def get_data(self):
        return eval(self.get_text())