import requests
import time

class build(object):
    """Class that encapsulates all jenkins related 'build' information
    
    Builds are executions of jobs and thus instances of this class are
    typically generated from the pyjen.job class.
    """
    def __init__ (self, url, user=None, password=None):
        self.__url = url
        self.__user = user
        self.__password = password
        
        if (self.__user != None):
            assert (self.__password != None)

    def get_url(self):
        return self.__url
    
    def get_build_number(self):
        r = requests.get(self.__url + "/api/python")
        assert(r.status_code == 200)
        data = eval(r.text)
        
        return data['number']
    
    def get_timestamp(self):
        r = requests.get(self.__url + "/api/python")
        assert(r.status_code == 200)
        data = eval(r.text)
        
        time_in_seconds = data['timestamp'] * 0.001
        
        return time.localtime(time_in_seconds)
    
    def is_building(self):
        r = requests.get(self.__url + "/api/python")
        assert (r.status_code == 200)
        data = eval(r.text)
        
        return data['building']
    
    #def is_in_queue(self):
    #    get path of parent job and look at its inQueue attribute
