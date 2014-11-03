from datetime import datetime
from pyjen.user import User

class ChangeSetItem(object):
    """Encapsulation of all info related to a single change in a changeset

    See also :py:mod:`pyjen.Changeset`
    """

    def __init__ (self, data, controller):
        """Constructor"""
        self._data = data
        self._controller = controller

    @property
    def author(self):
        """Person who committed this change to the associated SCM
        :rtype: :py:mod:`pyjen.User`
        """
        temp_data_io = self._controller.clone(self._data['author']['absoluteUrl'])
        return User(temp_data_io)

    @property
    def message(self):
        """SCM commit message associated with this change
        :rtype: :func:`str`
        """
        return self._data['msg']

    def __str__(self):
        outStr = "Author: {0}\nMessage: {1}\nRevision: {2}\n".format(
            self._data['author'],
            self._data['msg'],
            self._data['commitId']
        )
        outStr += "\nTouched Files:\n"
        for path in self._data['changes']:
            outStr += path['file'] + "\n"

        return outStr




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

        :returns: list of items detailing each change associated with this changeset
        :rtype: :func:`list` of :py:mod:`pyjen.ChangeSetItem` objects
        
        """
        retval = []

        for item in self.__data['items']:
            retval.append(ChangeSetItem(item, self._controller))

        return retval
    
    def __str__(self):    
        outStr = ""    
        changes = self.affected_items
        if len(changes) > 0:
            for change in changes:
                outStr += str(change)
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
