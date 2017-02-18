"""Primitives for interacting with Jenkins users"""
from pyjen.utils.jenkins_api import JenkinsAPI


class User(JenkinsAPI):
    """Interface to all primitives associated with a Jenkins user

    .. seealso:: :py:meth:`~.changeset.ChangesetItem.author`
    .. seealso:: :py:meth:`~.jenkins.Jenkins.find_user`

    :param str url: Full URL of the Jenkins REST API endpoint containing information about a particular user
    """

    def __init__(self, url):
        super(User, self).__init__(url)

    @property
    def user_id(self):
        """Gets the unique identifier for this user

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        return data['id']

    @property
    def full_name(self):
        """Gets the users full name, typically first and last names separated by a space

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        return data['fullName']

    @property
    def description(self):
        """Gets some descriptive text associated with the user. May be an empty string if no description found.

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        return data['description'] if data['description'] is not None else ''

    @property
    def email(self):
        """Gets this users' email address as reported by Jenkins. May be None if no email on record for user.

        :rtype: :class:`str`
        """
        data = self.get_api_data()
        for prop in data['property']:
            if 'address' in prop:
                return prop['address']

        return None

if __name__ == "__main__":  # pragma: no cover
    pass
