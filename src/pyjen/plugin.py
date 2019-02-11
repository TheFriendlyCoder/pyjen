"""Interface for interacting with Jenkins plugins"""
import requests
from tqdm import tqdm
import os


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
        """Gets a URL where the version of this plugin installed on Jenkins may be downloaded"""
        download_template = "http://updates.jenkins-ci.org/download/plugins/{0}/{1}/{0}.hpi"

        return download_template.format(self.short_name, self.version)

    @property
    def latest_download_url(self):
        """Gets a URL where the latest version of this plugin can be downloaded"""
        download_template = "http://updates.jenkins-ci.org/latest/{0}.hpi"
        return download_template.format(self.short_name)

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
                tmp = {
                    'shortName': cur_dep['shortName'],
                    'version': cur_dep['version']
                }
                retval.append(tmp)
        return retval

    def download(self, output_folder, overwrite=False, show_progress=False, get_latest=False):
        """Downloads the plugin installation file for this Jenkins server plugin to a local folder
        
        :param str output_folder: path where the downloaded plugin file will be stored
        :param bool overwrite: indicates whether existing plugin files should be overwritten in the target folder
        :param bool show_progress: indicates whether a progress bar should be displayed as the plugin is downloaded
        :param bool get_latest: 
            indicates whether the latest version of this plugin should be downloaded. If false,
            the version currently installed on this Jenkins instance is downloaded.
        """

        # Construct an absolute path for our output file based on a meaningful naming convention
        output_filename = "{0}-{1}.hpi".format(self.short_name, self.version)
        output_file = os.path.join(output_folder, output_filename)

        # See if we need to overwrite the output file or not...
        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError("Output file already exists: " + output_file)

        # Make sure our output folder exists...
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Stream the download of the plugin installer from the online Jenkins plugin database
        response = requests.get(self.download_url, stream=True, verify=False)

        # Download data in 100KB chunks
        buff_size = 100 * 1024

        # Configure our progress indicator
        file_size = int(response.headers['content-length'])
        with tqdm(desc=output_filename, unit='B', unit_scale=True, disable=not show_progress,
                  total=file_size) as progress:
            # Save our streaming data
            with open(output_file, "wb") as handle:
                for data in response.iter_content(buff_size):
                    progress.update(buff_size)
                    handle.write(data)

if __name__ == "__main__":
    pass
