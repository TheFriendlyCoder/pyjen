"""Primitives for interacting with Jenkins users"""
import json


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

    def __str__(self):
        return json.dumps(self._api.get_api_data(), indent=4)

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

    def create_api_token(self, token_name):
        """Creates a new REST API access token for the user

        NOTE: the API token can not be retrieved independently from the REST
        API, so make sure to store / preserve the API token returned from this
        method for later use.

        Implementation is based on the curl examples found here:
        https://support.cloudbees.com/hc/en-us/articles/115003090592-How-to-re-generate-my-Jenkins-user-token#usingtherestapi

        Args:
            token_name (str): friendly name associated with the new token

        Returns:
            str: copy of the newly generated token
        """
        params = {
            "data": {
                "newTokenName": token_name
            }
        }
        temp_url = self._api.url + \
                   "descriptorByName/jenkins.security.ApiTokenProperty/" \
                   "generateNewToken"
        resp = self._api.post(temp_url, params)

        data = resp.json()
        if data.get("status", "").lower() != "ok":
            raise Exception(
                "Error creating API token: " + data.get("status", ""))

        return data["data"]["tokenValue"]


if __name__ == "__main__":  # pragma: no cover
    pass
