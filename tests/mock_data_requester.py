class file_based_requester(object):
    def __init__ (self, path_to_file):
        f = open(path_to_file, "r")
        self.__text = f.read()
        f.close()
        
    def get_text(self, sub_url=None):
                
        return self.__text
        
    def get_data(self, sub_url=None):
        return eval(self.get_text(sub_url))
    
    def get_headers(self, sub_url=None):
        pass
    
    def post(self, sub_url=None, args=None):
        pass
    
class post_validate_requester:
    __expected_url = ""
    def __init__(self, expected_url):
        self.__expected_url=expected_url
    def post (self, sub_url=None, args=None):
        print (self.__expected_url)
        print (sub_url)
        assert(sub_url == self.__expected_url)
        return