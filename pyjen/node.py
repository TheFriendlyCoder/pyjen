import requests
import time
import urllib

class node:
    def __init__(self, url):
        self.__url = url
        
    def get_url(self):
        return self.__url
    
    def get_name(self):
        r = requests.get(self.__url + '/api/python')
        assert (r.status_code == 200)
        data = eval(r.text)
        
        return data['displayName']
    
    def is_offline(self):
        r = requests.get(self.__url + '/api/python')
        assert(r.status_code == 200)
        data = eval(r.text)
        
        return data['offline']
    
    def toggle_offline(self, message):
        r = requests.post(self.__url + "/toggleOffline?offlineMessage=" + urllib.quote(message))
        assert(r.status_code == 200)
        
    def is_idle(self):
        r = requests.get(self.__url + '/api/python')
        assert(r.status_code == 200)
        data = eval(r.text)
        
        return data['idle']
    
    def wait_for_idle(self):
        while not self.is_idle():
            time.sleep(5)
