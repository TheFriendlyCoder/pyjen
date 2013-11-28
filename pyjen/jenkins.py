import requests
import json
from view import view
from node import node
from job import job


class jenkins:
    """Python wrapper managing a Jenkins primary dashboard
    
    Generally you should use this class as the primary entry
    point to the PyJen APIs. 
    """
    def __init__ (self, url):
        self.__url = url
        
    def get_url(self):
        return self.__url
    
    def get_views(self):
        r = requests.get(self.__url + '/api/python')
        assert(r.status_code == 200)
        data = eval(r.text)
        
        raw_views = data['views']
        retval = []
        for v in raw_views:
            retval.append(view(v['url']))
                        
        return retval
    
    def get_default_view(self):
        r = requests.get(self.__url + '/api/python')
        assert (r.status_code == 200)
        
        data = eval(r.text)
        
        default_view = data['primaryView']
        return view(default_view['url'], default_view['name'])
    
    def get_nodes(self):
        r = requests.get(self.__url + '/computer/api/python')
        assert(r.status_code == 200)
        data = eval(r.text)
        
        nodes = data['computer']
        retval = []
        for n in nodes:
            if n['displayName'] == 'master':
                retval.append(node(self.__url + '/computer/(master)'))
            else:
                retval.append(node(self.__url + '/computer/' + n['displayName']))
                        
        return retval
    
    def get_version(self):
        r = requests.get(self.__url)
        assert(r.status_code == 200)
        if not 'x-jenkins' in r.headers:
            return "Unknown"
        else:
            return r.headers['x-jenkins']
        
    def prepare_shutdown(self):
        r = requests.post(self.__url + "/quietDown")
        assert(r.status_code == 200)
    
    def cancel_shutdown(self):
        r = requests.post(self.__url + "/cancelQuietDown")
        assert(r.status_code == 200)    
    
    def is_shutting_down(self):
        r = requests.get(self.__url + "/api/python")
        assert(r.status_code == 200)
        
        data = eval(r.text)
        return data['quietingDown']
      
    def find_job(self, job_name):
        r = requests.get(self.__url + "/api/python")
        assert(r.status_code == 200)
        
        data = eval(r.text)
        tjobs = data['jobs']
    
        for tjob in tjobs:
            if tjob['name'] == job_name:
                return job(tjob['url'])
        
        return None
    
    def find_view(self, view_name):
        r = requests.get(self.__url + '/api/python')
        assert(r.status_code == 200)
        data = eval(r.text)
        
        raw_views = data['views']
        
        for v in raw_views:
            if v['name'] == view_name:
                return view(v['url'])
                        
        return None

    def create_view(self, view_name, view_type = view.LIST_VIEW):
        #TODO: consider rethinking this method. Perhaps it'd be better
        #      suited to the view class. Alaternatively, maybe we just
        #      construct the view class externally then insert it
        #      onto the dashboard here .... not sure.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }
        
        args = {}
        args['data'] = data
        args['headers'] = headers
        
        r = requests.post(self.__url + "/createView", **args)
        assert(r.status_code == 200)
        
        


    
        
if __name__ == '__main__':

    j = jenkins("http://localhost:8080")
