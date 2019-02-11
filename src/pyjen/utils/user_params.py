"""Interfaces for parsing user defined configuration parameters"""
import os
import platform
from six.moves import configparser
from pyjen.exceptions import InvalidUserParamsError


class JenkinsConfigParser(configparser.ConfigParser):  # pylint: disable=too-many-ancestors
    """ Interface to the PyJen user configuration file

        ::

            Config File Format
            ==================
            [http://jenkins_server_url]
            username=MyUserName
            password=MyPassword

            [http://another_jenkins_url]
            username=other_username
            password=other_password

            #Anonymous access can be defined like this
            [http://some_jenkins_url]
            username=
            password=

        For more details on the general format of the config file see these links:
            https://wiki.python.org/moin/ConfigParserExamples
            https://docs.python.org/2/library/configparser.html
        """
    def get_credentials(self, jenkins_url):
        """Gets the authentication credentials for a given Jenkins URL

        :param str jenkins_url: arbitrary URL to the Jenkins REST API to retrieve credentials for
            URL may point to any arbitrary artifact on the Jenkins REST API. The credentials
            will be matched based on the section headers in any of the associated config files
        :returns: username and password for the given URL. Will return None if no credentials found.
        :rtype: :func:`tuple`
        """
        section_name = None
        for cur_section in self.sections():
            if jenkins_url.startswith(cur_section):
                section_name = cur_section
                break

        if not section_name:
            return None

        temp_username = None
        temp_password = None
        if self.has_option(section_name, "username"):
            temp_username = self.get(section_name, "username")
        if self.has_option(section_name, "password"):
            temp_password = self.get(section_name, "password")

        if not temp_username and not temp_password:
            return None

        if not temp_username:
            raise InvalidUserParamsError("No username specified for password under " + section_name)
        if not temp_password:
            raise InvalidUserParamsError("No password specified for user " + temp_username + " under " + section_name)
        return temp_username, temp_password

    @staticmethod
    def get_default_configfiles():
        """Gets a list of potential locations where PyJen config files may be found

        :returns: list of paths to be searched
        :rtype: :class:`list`
        """
        if platform.system() == "Windows":
            config_filename = "pyjen.cfg"
        else:
            config_filename = ".pyjen"

        # NOTE: The ConfigParser's search order is inverted, so we put
        # the least privileged location first
        retval = []
        # Second search location is the users home folder
        retval.append(os.path.join(os.path.expanduser("~"), config_filename))
        # First search location is the current working folder
        retval.append(os.path.join(os.getcwd(), config_filename))

        return retval

if __name__ == "__main__":  # pragma: no cover
    pass
