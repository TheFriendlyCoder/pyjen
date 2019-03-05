"""Primitives for interacting with Jenkins users"""


class User(object):
    """Interface to all primitives associated with a Jenkins user

    .. seealso:: :py:meth:`~.changeset.ChangesetItem.author`
    .. seealso:: :py:meth:`~.jenkins.Jenkins.find_user`

    :param api:
        Pre-initialized connection to the Jenkins REST API
    :type api: :class:`~/utils/jenkins_api/JenkinsAPI`
    """

    def __init__(self, api):
        super(User, self).__init__()
        self._api = api

    @property
    def user_id(self):
        """Gets the unique identifier for this user

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['id']

    @property
    def full_name(self):
        """the users first and last names separated by a space

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['fullName']

    @property
    def description(self):
        """descriptive text associated with the user.

        May be an empty string if no description found.

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        return data['description'] if data['description'] is not None else ''

    @property
    def email(self):
        """Gets this users' email address as reported by Jenkins.

        May be None if no email on record for user.

        :rtype: :class:`str`
        """
        data = self._api.get_api_data()
        for prop in data['property']:
            if 'address' in prop:
                return prop['address']

        return None


if __name__ == "__main__":  # pragma: no cover
    pass
