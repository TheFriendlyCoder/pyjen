"""Primitives for interacting with SCM changesets"""
import json
from pyjen.user import User


class Changeset:
    """Represents a set of SCM revisions associated with a
    :class:`~.build.Build` of a :class:`~.job.Job`.

    See :py:meth:`~.build.Build.changeset` for details.
    """

    def __init__(self, api, data):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
            data (dict):
                Dictionary of data elements typically parsed from the
                "changeSet" node of a builds source data as provided by the
                Jenkins REST API.
        """
        assert 'items' in data
        assert 'kind' in data
        self._api = api
        self._data = data

    @property
    def affected_items(self):
        """list (ChangesetItem): details of the individual commits associated
        with a build"""
        retval = []

        for item in self._data['items']:
            retval.append(ChangesetItem(self._api, item))

        return retval

    def __str__(self):
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
        """bool: True if there are SCM changes associated with this changeset,
        False if not"""
        return bool(self._data['items'])

    @property
    def scm_type(self):
        """str: name of the SCM tool associated with this change"""
        return self._data['kind']


class ChangesetItem(object):
    """details of each SCM revision associated with a given :class:`Changeset`
    """
    def __init__(self, api, data):
        """
        Args:
            data (dict):
                Dictionary of attributes describing a single commit.
        """
        self._api = api
        self._data = data

    @property
    def author(self):
        """User: Person who committed this change to the associated SCM"""
        return User(self._api.clone(self._data['author']['absoluteUrl']))

    @property
    def message(self):
        """str: SCM commit message associated with this change"""
        return self._data['msg']

    @property
    def commit_id(self):
        """str: the SCM ref spec associated with this specific change"""
        return self._data["commitId"]

    @property
    def affected_files(self):
        """list (str): list of files modified in this commit"""
        retval = list()
        for cur_item in self._data["paths"]:
            retval.append(cur_item["file"])
        return retval

    def __str__(self):
        return json.dumps(self._data, indent=4)


if __name__ == "__main__":  # pragma: no cover
    pass
