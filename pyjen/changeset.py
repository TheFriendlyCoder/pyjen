"""Primitives for interacting with SCM changesets"""
from pyjen.user import User
from pyjen.utils.jenkins_api import JenkinsAPI
from pyjen.utils.datarequester import DataRequester


class Changeset(object):
    """manages the interpretation of the "changeSet" properties of a Jenkins build

    .. seealso:: :class:`~.build.Build`

    """

    def __init__(self, data):
        """
        :param dict data:
            Dictionary of data elements typically parsed from the "changeSet" node
            of a builds source data as provided by the Jenkins REST API. Should have
            at least the following keys:

            * **'kind'** - string describing the SCM tool associated with this change all changes reported by this
              object are expected to be stored in the same SCM tool
            * **'items'** - list of 0 or more actual changesets included in the associated build
        :param controller: object controlling access to Jenkins API
        :type controller: :class:`~.utils.datarequester.DataRequester`
        """

        assert 'items' in data.keys()
        assert 'kind' in data.keys()

        self._data = data

    @property
    def affected_items(self):
        """gets details of the changes associated with the parent build

        :returns: list of 0 or more items detailing each change associated with this Changeset
        :rtype: :class:`list` of :class:`ChangesetItem` objects
        """
        retval = []

        for item in self._data['items']:
            retval.append(ChangesetItem(item))

        return retval

    def __str__(self):
        retval = ""
        changes = self.affected_items
        if len(changes) > 0:
            for change in changes:
                retval += str(change)
        else:
            retval = "No Changes\n"
        return retval

    @property
    def has_changes(self):
        """Checks whether or not there are any SCM changes

        :returns: True if changes have been found, False if not
        :rtype: :class:`bool`
        """
        return bool(self._data['items'])

    @property
    def scm_type(self):
        """Gets the name of the SCM tool associated with this change

        :returns: Name of the SCM tool associated with this change
        :rtype: :class:`str`
        """
        return self._data['kind']


class ChangesetItem(object):
    """Encapsulates all info related to a single change in a Changeset

    .. seealso:: :class:`Changeset`
    """

    def __init__(self, data):
        """
        :param dict data: Dictionary of attributes describing this single changeset
        :param controller: Interface to the Jenkins API
        :type controller: :class:`~.utils.datarequester.DataRequester`"""
        self._data = data

    @property
    def author(self):
        """
        :returns: Person who committed this change to the associated SCM
        :rtype: :class:`~.user.User`
        """
        http_io = DataRequester(self._data['author']['absoluteUrl'], JenkinsAPI.ssl_verify_enabled)
        http_io.credentials = JenkinsAPI.creds
        return User(http_io)

    @property
    def message(self):
        """
        :returns: SCM commit message associated with this change
        :rtype: :class:`str`
        """
        return self._data['msg']

    def __str__(self):
        retval = "Author: {0}\nMessage: {1}\nRevision: {2}\n".format(
            self._data['author'],
            self._data['msg'],
            self._data['commitId']
        )
        retval += "\nTouched Files:\n"
        for path in self._data['changes']:
            retval += path['file'] + "\n"

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
