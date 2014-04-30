class file_based_requester(object):
    def __init__ (self, path_to_file):
        f = open(path_to_file, "r")
        self.__text = f.read()
        f.close()
        
    def get_text(self, sub_url=None):
                
        return self.__text
        
    def get_data(self, sub_url=None):
        return eval(self.get_text(sub_url))
    
    def get_api_data(self, sub_url=None):
        return eval(self.get_text(sub_url))
    
    def get_headers(self, sub_url=None):
        pass
    
    def post(self, sub_url=None, args=None):
        pass
    
class dictionary_based_requester(object):
    """Mock HTTP IO class that manages a static dictionary of source data"""
    def __init__ (self, source_data):
        """constructor
        
        Parameters
        ------------------
        source_data : dictionary
            static dictionary of data to be exposed by the get_api_data
            method to classes under test.
        """
        self.__source_data=source_data
    
    def get_api_data(self, url=None):
        """Exposes mock API data provided by the constructor
        
        Parameters
        -------------
        url - ignored
        """
        return self.__source_data
    
class post_validate_requester:
    __expected_url = ""
    def __init__(self, expected_url):
        self.__expected_url=expected_url
    def post (self, sub_url=None, args=None):
        print (self.__expected_url)
        print (sub_url)
        assert(sub_url == self.__expected_url)
        return
    