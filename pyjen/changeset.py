from datetime import datetime

class changeset (object):
    """class that manages the interpretation of the "changeSet" properties of a Jenkins build"""

    def __init__(self, data):
        """constructor
        
        Parameters
        ----------
        data : dictionary
            Dictionary of data elements typically parsed from the "changeSet" node
            of a builds source data as provided by the Jenkins REST API. Should have
            at least the following keys (NOTE: Some addins provide extra properties
            not explicitly exposed by this class)
            
            'kind' - string describing the SCM tool associated with this change
                   - all changes reported by this object are expected to be stored
                     in the same SCM tool
                     
            'items' - list of 0 or more actual changesets included in the associated build
        """

        assert('items' in data.keys())
        assert('kind' in data.keys())
    
        self.__data = data

    def get_affected_items(self):
        """gets details of the changes associated with the parent build

        Return
        ------
        list[dictionary]
            list of the details of 0 or more changes in this set
            properties:
            'author' - type: string 
                - name of the person who committed the change
            'authorUrl' - type: string
                - url to the users profile information as managed by the Jenkins dashboard
            'commitId' - type: string
                - unique identifier assigned by the SCM tool associated with this change
                - NOTE: This attribute may or may not be numeric
            'message' - type: string
                - commit log describing each change
            'time' - type: datetime
                - time stamp of when the commit was made
            'changes' - type: list[dictionary]
                - list of 1 or more files or folders included in this changeset
                - each element has two properties:
                    - 'editType' - string describing whether the edit was an addition, modification or removal
                    - 'file' - the path and file name that was modified
                            - paths are relative the root of the source repository for the associated SCM tool
        """
        retval = []

        for item in self.__data['items']:
            #TODO: Add some asserts() here to validate certain assumptions in my script
            #      like the fact that commitID and ID are always the same. Similarly,
            #      author->fullName should be identical to the user attribute. Also,
            #      affectedPaths == paths['file'].
            #
            #      The reason being, if these assumptions prove invalid in production they
            #      will throw an error right away giving us something to look at and
            #      investigate.
            tmp = {}
            tmp['author'] = item['author']['fullName']
            tmp['authorUrl'] = item['author']['absoluteUrl']
            tmp['commitId'] = item['commitId']
            tmp['message'] = item['msg']
            tmp['time'] = datetime.fromtimestamp(item['timestamp'] * 0.001)
            tmp['changes'] = item['paths']
            retval.append(tmp)
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
        
        Return
        ------
            boolean
                True : changes have been found
                False : there are no changes        
        """
        if (self.__data['items']):
            return True
        else:
            return False
        
    def get_scm_type(self):
        """Gets the name of the SCM tool associated with this change
        
        Return
        ------
        string
            Name of the SCM tool associated with this change
        """
        return self.__data['kind']
