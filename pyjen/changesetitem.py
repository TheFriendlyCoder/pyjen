"""Primitives for interacting with SCM changesets associated with a build"""
from pyjen.user import User


class ChangesetItem(object):
    """Encapsulates all info related to a single change in a Changeset

    .. seealso:: :class:`~.changeset.Changeset`
    """

    def __init__(self, data, controller):
        """
        :param dict data: Dictionary of attributes describing this single changeset
        :param controller: Interface to the Jenkins API
        :type controller: :class:`~.utils.datarequester.DataRequester`"""
        self._data = data
        self._controller = controller

    @property
    def author(self):
        """
        :returns: Person who committed this change to the associated SCM
        :rtype: :class:`~.user.User`
        """
        temp_data_io = self._controller.clone(self._data['author']['absoluteUrl'])
        return User(temp_data_io)

    @property
    def message(self):
        """
        :returns: SCM commit message associated with this change
        :rtype: :class:`str`
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

if __name__ == "__main__":  # pragma: no cover
    pass
