import requests
from job import job

class view(object):
    #Class names for all supported view types
    LIST_VIEW = 'hudson.model.ListView'
    
    def __init__ (self, url, user=None, password=None):
        self.__url = url
        self.__user = user
        self.__password = password
        
        if (self.__user != None):
            assert (self.__password != None)
        
    def get_url(self):
        return self.__url
    
    def get_name(self):
        r = requests.get(self.__url + "/api/python")
        assert(r.status_code == 200)
        data = eval(r.text)
        
        return data['name']
        
    def get_jobs (self):
        r = requests.get(self.__url + "/api/python")
        data = eval(r.text)
        
        view_jobs = data['jobs']

        retval = []
        for j in view_jobs:        
            retval.append(job(j['url']))
            
        return retval
    
    def get_config_xml(self):
        r = requests.get(self.__url + "/config.xml")
        return r.text
    
    def set_config_xml(self, new_xml):
        headers = {'Content-Type': 'text/xml'}
        args = {}
        args['data'] = new_xml
        args['headers'] = headers
        
        r = requests.post(self.__url + "/config.xml", **args)
        assert (r.status_code == 200)
