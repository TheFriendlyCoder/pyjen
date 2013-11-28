import requests

class data_requester:
    def __init__ (self, url, user=None, password=None):
        self.__url = url
        self.__user = user
        self.__password = password
    
    def get_data(self):
        if self.__user != None:
            r = requests.get(self.__url, auth=(self.__user, self.__password))
        else:
            r = requests.get(self.__url)
        
        #todo: improve error detection and reporting    
        assert(r.status_code == 200)
        
        return eval(r.text)
