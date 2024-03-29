"""Interface for interacting with Jenkins plugins"""
import os
import json
import requests


class Plugin:
    """Abstraction around one Jenkins plugin"""
    def __init__(self, plugin_config):
        """
        Args:
            plugin_config (dict):
                Parsed Jenkins API data associated with this plugin. Typically
                this content is produced by the Jenkins plugin manager API.
                See :class:`~.plugin_manager.PluginManager` for details.
        """
        self._config = plugin_config

    def __repr__(self):
        return json.dumps(self._config, indent=4)

    @property
    def long_name(self):
        """str: the descriptive name of this plugin"""
        return self._config['longName']

    @property
    def short_name(self):
        """str: the abbreviated name of this plugin"""
        return self._config['shortName']

    @property
    def version(self):
        """str: the version of this plugin"""
        return self._config['version']

    @property
    def enabled(self):
        """bool: checks to see if this plugin is enabled or not"""
        return self._config['enabled']

    @property
    def download_url(self):
        """str: URL where the version of this plugin may be downloaded"""
        download_template = \
            "http://updates.jenkins-ci.org/download/plugins/{0}/{1}/{0}.hpi"

        return download_template.format(self.short_name, self.version)

    @property
    def latest_download_url(self):
        """str: URL where the latest version of this plugin can be downloaded"""
        download_template = "http://updates.jenkins-ci.org/latest/{0}.hpi"
        return download_template.format(self.short_name)

    @property
    def info_url(self):
        """str: the URL for the website describing the use of this plugin"""
        return self._config['url']

    @property
    def required_dependencies(self):
        """list (dict): metadata describing the plugins this plugin depends on.
        Nested dictionaries contain the 'shortName' and 'version' fields for use
        by the caller."""
        retval = []
        for cur_dep in self._config['dependencies']:
            if not cur_dep['optional']:
                tmp = {
                    'shortName': cur_dep['shortName'],
                    'version': cur_dep['version']
                }
                retval.append(tmp)
        return retval

    def download(self, output_folder, overwrite=False):
        """Downloads the plugin installation file for this plugin

        Args:
            output_folder (str):
                path where the downloaded plugin file will be stored
            overwrite (bool):
                indicates whether existing plugin files should be overwritten in
                the target folder
        """
        # Construct an absolute path for our output file based on a meaningful
        # naming convention
        output_filename = f"{self.short_name}-{self.version}.hpi"
        output_file = os.path.join(output_folder, output_filename)

        # See if we need to overwrite the output file or not...
        if os.path.exists(output_file) and not overwrite:
            msg = "Output file already exists: " + output_file
            raise FileExistsError(msg)

        # Make sure our output folder exists...
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Stream the download of the plugin installer from the online Jenkins
        # plugin database
        # TODO: update this code to use the same session object that is used
        #       for the Jenkins serve connection
        response = requests.get(self.download_url, stream=True, verify=True)

        # Download data in 100KB chunks
        buff_size = 100 * 1024

        # Save our streaming data
        with open(output_file, "wb") as handle:
            for data in response.iter_content(buff_size):
                handle.write(data)


if __name__ == "__main__":  # pragma: no cover
    pass
