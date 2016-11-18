"""Interface for interacting with Jenkins plugins"""


class Plugin(object):
    """Abstraction around one Jenkins plugin"""
    def __init__(self, plugin_config):
        """Constructor
        :param dict plugin_config:
            Parsed Jenkins API data associated with this plugin. Typically this content is produced by the
            Jenkins plugin manager API. See :class:`~.plugin_manager.PluginManager` for details.
        """
        self._config = plugin_config

    @property
    def long_name(self):
        """Gets the descriptive name of this plugin"""
        return self._config['longName']

    @property
    def short_name(self):
        """Gets the abbreviated name of this plugin"""
        return self._config['shortName']

    @property
    def version(self):
        """Gets the version of this plugin"""
        return self._config['version']

    @property
    def enabled(self):
        """Checks to see if this plugin is enabled or not"""
        return self._config['enabled']

    @property
    def download_url(self):
        """Gets a URL where this version of this plugin may be downloaded"""
        download_template = "http://updates.jenkins-ci.org/download/plugins/{0}/{1}/{0}.hpi"

        return download_template.format(self.short_name, self.version)

    @property
    def info_url(self):
        """Gets the URL for the website describing the use of this plugin"""
        return self._config['url']

    @property
    def required_dependencies(self):
        """Gets a list of the dependencies this plugin needs in order to work correctly

        :returns: list of 0 or more dictionaries containing the 'shortName' and 'version' of all dependencies
        """
        retval = []
        for cur_dep in self._config['dependencies']:
            if not cur_dep['optional']:
                tmp = {}
                tmp['shortName'] = cur_dep['shortName']
                tmp['version'] = cur_dep['version']
                retval.append(tmp)
        return retval

if __name__ == "__main__":
    pass
