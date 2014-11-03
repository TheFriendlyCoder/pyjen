from datetime import datetime
from pyjen.user import User

class ChangeSetItem(object):
    def __init__ (self, data, controller):
        self._data = data
        self._controller = controller

    @property
    def author(self):
        temp_data_io = self._controller.clone(self._data['author']['absoluteUrl'])
        return User(temp_data_io)
    @property
    def message(self):
        return self._data['msg']


class changeset (object):
    """class that manages the interpretation of the "changeSet" properties of a Jenkins build"""

    def __init__(self, data, controller):
        """constructor
        
        :param dict data: 
            Dictionary of data elements typically parsed from the "changeSet" node
            of a builds source data as provided by the Jenkins REST API. Should have
            at least the following keys (NOTE: Some addins provide extra properties
            not explicitly exposed by this class) 
            'kind' - string describing the SCM tool associated with this change
            all changes reported by this object are expected to be stored
            in the same SCM tool     
            'items' - list of 0 or more actual changesets included in the associated build
        
        """

        assert('items' in data.keys())
        assert('kind' in data.keys())
    
        self.__data = data
        self._controller = controller

    @property
    def affected_items(self):
        """gets details of the changes associated with the parent build

        :returns:
        list of the details of 0 or more changes in this set properties:
        'author' - :func:`str`
            - name of the person who committed the change
        'authorUrl' - :func:`str`
            - url to the users profile information as managed by the Jenkins dashboard
        'commitId' - :func:`str`
            - unique identifier assigned by the SCM tool associated with this change
            - NOTE: This attribute may or may not be numeric
        'message' - type: :func:`str`
            - commit log describing each change
        'time' - type: :class:`datetime.datetime`
            - time stamp of when the commit was made
        'changes' - type: :func:`list` of :func:`dictionary`
            - list of 1 or more files or folders included in this changeset
            - each element has two properties:
                - 'editType' - string describing whether the edit was an addition, modification or removal
                - 'file' - the path and file name that was modified
                        - paths are relative the root of the source repository for the associated SCM tool
        
        :rtype: :func:`list` of :func:`dict` objects
        
        """
        retval = []

        for item in self.__data['items']:
            retval.append(ChangeSetItem(item, self._controller))

        return retval
    
    def __str__(self):    
        outStr = ""    
        changes = self.get_affected_items()
        if (changes):
            for change in changes:
                outStr += "Author: %s\n"% change['author']
                outStr += "Message: %s\n"% change['message']
                outStr += "Revision: %s\n"% change['commitId']
            
                outStr += "\nTouched Files:\n"
                for path in change['changes']:
                    outStr += path['file']
                    outStr += "\n"
                outStr += "\n"
        else:
            outStr = "No Changes\n"                       
        return outStr
    
    def has_changes(self):
        """Checks whether or not there are any SCM changes
        
        :returns:
                True : changes have been found
                False : there are no changes        
        :rtype: :func:`bool`
        """
        if (self.__data['items']):
            return True
        else:
            return False
        
    def get_scm_type(self):
        """Gets the name of the SCM tool associated with this change
        
        :returns: Name of the SCM tool associated with this change
        :rtype: :func:`str`
        """
        return self.__data['kind']
