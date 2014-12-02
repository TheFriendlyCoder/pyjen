from pyjen.user import User

class ChangesetItem(object):
    """Encapsulation of all info related to a single change in a Changeset

    See also :py:mod:`pyjen.Changeset`
    """

    def __init__(self, data, controller):
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

if __name__ == "__main__":  # pragma: no cover
    pass
