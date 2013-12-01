class changeset (object):
    def __init__(self, obj):
        self.__obj = obj
        pass
    
    def get_items(self):
        print self.__obj
        
