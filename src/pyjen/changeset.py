"""Primitives for interacting with SCM changesets"""
import json
from pyjen.user import User


class Changeset:
    """Represents a set of changes associated with a build of a Jenkins job

    .. seealso:: :class:`~.build.Build`

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~.utils.jenkins_api.JenkinsAPI`
    :param dict data:
        Dictionary of data elements typically parsed from the "changeSet" node
        of a builds source data as provided by the Jenkins REST API. Should have
        at least the following keys:

        * **'kind'** - string describing the SCM tool associated with this set
                       of changes.
        * **'items'** - list of 0 or more SCM revisions associated with this
                        change
    """

    def __init__(self, api, data):
        assert 'items' in data
        assert 'kind' in data
        self._api = api
        self._data = data

    @property
    def affected_items(self):
        """gets details of the changes associated with the parent build

        :returns:
            list of 0 or more revisions detailing each change associated with
            this Changeset
        :rtype: :class:`list` of :class:`ChangesetItem` objects
        """
        retval = []

        for item in self._data['items']:
            retval.append(ChangesetItem(self._api, item))

        return retval

    def __str__(self):  # pragma: no cover
        retval = json.dumps(self._data, indent=4)
        changes = self.affected_items
        if changes:
            for change in changes:
                retval += str(change)
        else:
            retval = "No Changes"
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
    """details of each SCM revision associated with a given :class:`Changeset`

    .. seealso:: :class:`Changeset`

    :param dict data:
        Dictionary of attributes describing this revision.
        Required keys are as follows:

        * author: :class:`dict` describing the Jenkins user who committed this
                  change
        * msg: :class:`str` representing the commit messages from the SCM tool
               associated with this change
        * commitId: :class:`str` representing the revision number of the change
                    provided by the SCM tool
        * changes: :class:`list` of :class:`dict` describing the files modified
                   by this change
    """

    def __init__(self, api, data):
        self._api = api
        self._data = data

    @property
    def author(self):
        """
        :returns: Person who committed this change to the associated SCM
        :rtype: :class:`~.user.User`
        """
        return User(self._api.clone(self._data['author']['absoluteUrl']))

    @property
    def message(self):
        """
        :returns: SCM commit message associated with this change
        :rtype: :class:`str`
        """
        return self._data['msg']

    @property
    def commit_id(self):
        """Gets the SCM revision associated with this specific change

        :rtype: :class:`str`
        """
        return self._data["commitId"]

    @property
    def affected_files(self):
        """Gets a list of files modified in this commit

        :rtype: :class:`list` of :class:`str`
        """
        retval = list()
        for cur_item in self._data["paths"]:
            retval.append(cur_item["file"])
        return retval

    def __str__(self):  # pragma: no cover
        return json.dumps(self._data, indent=4)


if __name__ == "__main__":  # pragma: no cover
    pass
