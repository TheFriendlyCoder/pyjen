"""Primitives for interacting with Jenkins users"""


class User:
    """Interface to all primitives associated with a Jenkins user

    See :py:meth:`~.changeset.ChangesetItem.author` and
    :py:meth:`~.jenkins.Jenkins.find_user` for examples on where this class
    is used.
    """

    def __init__(self, api):
        """
        Args:
            api (JenkinsAPI):
                Pre-initialized connection to the Jenkins REST API
        """
        super().__init__()
        self._api = api

    @property
    def user_id(self):
        """str: the unique identifier for this user"""
        data = self._api.get_api_data()
        return data['id']

    @property
    def full_name(self):
        """str: the users first and last names separated by a space"""
        data = self._api.get_api_data()
        return data['fullName']

    @property
    def description(self):
        """str: descriptive text associated with the user. May be an empty
        string."""
        data = self._api.get_api_data()
        return data['description'] if data['description'] is not None else ''

    @property
    def email(self):
        """str: Gets this users' email address as reported by Jenkins. May be
        None if no email on record for user."""
        data = self._api.get_api_data()
        for prop in data['property']:
            if 'address' in prop:
                return prop['address']

        return None


if __name__ == "__main__":  # pragma: no cover
    pass
