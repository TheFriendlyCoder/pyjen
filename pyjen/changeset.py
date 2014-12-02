from pyjen.changesetitem import ChangesetItem


class Changeset (object):
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
    
        self._data = data
        self._controller = controller

    @property
    def affected_items(self):
        """gets details of the changes associated with the parent build

        :returns: list of items detailing each change associated with this Changeset
        :rtype: :func:`list` of :py:mod:`pyjen.ChangesetItem` objects
        
        """
        retval = []

        for item in self._data['items']:
            retval.append(ChangesetItem(item, self._controller))

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

    @property
    def has_changes(self):
        """Checks whether or not there are any SCM changes
        
        :returns:
                True : changes have been found
                False : there are no changes        
        :rtype: :func:`bool`
        """
        if (self._data['items']):
            return True
        else:
            return False

    @property
    def scm_type(self):
        """Gets the name of the SCM tool associated with this change
        
        :returns: Name of the SCM tool associated with this change
        :rtype: :func:`str`
        """
        return self._data['kind']

if __name__ == "__main__":  # pragma: no cover
    pass
