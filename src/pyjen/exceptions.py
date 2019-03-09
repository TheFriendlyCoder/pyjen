"""All PyJen specific exception declarations"""


class PyJenError(Exception):
    """Base class for all PyJen related exceptions"""
    def __init__(self):
        super(PyJenError, self).__init__()


class InvalidUserParamsError(PyJenError):
    """Exception caused by invalid parameters in the user configuration file"""
    def __init__(self, msg):
        """constructor

        :param str msg: Descriptive message associated with this exception
        """
        super(InvalidUserParamsError, self).__init__()
        self.__msg = msg

    def __str__(self):
        return "Error parsing config file: " + self.__msg


class InvalidJenkinsURLError(PyJenError):
    """Exception raised when attempting to connect to a URL that doesn't point
    to a valid Jenkins REST API"""
    def __init__(self, msg, url):
        """constructor

        :param str msg: Descriptive message associated with this exception
        :param str url: URL in question that does not point to a valid Jenkins
            REST API
        """
        super(InvalidJenkinsURLError, self).__init__()
        self.__msg = msg
        self.__url = url

    def __str__(self):
        return "Error connecting to Jenkins API via " + self.__url + ": \n\t" +\
            self.__msg


class InvalidParameterError(PyJenError):
    """Exception raised when the caller provides an invalid value as an input
        parameter to a PyJen method call"""

    def __init__(self, msg):
        """Constructor

        :param str msg: Descriptive message associated with this exception
        """
        super(InvalidParameterError, self).__init__()

        self.__msg = msg

    def __str__(self):
        return self.__msg


class NotYetImplementedError(PyJenError):
    """Exception thrown from methods that are not yet implemented"""

    def __init__(self):
        """constructor"""
        super(NotYetImplementedError, self).__init__()


class PluginNotSupportedError(NotImplementedError):
    """Error with details about a plugin that was not found"""
    def __init__(self, message, plugin_name):
        """Constructor

        :param str message: description of the error
        :param str plugin_name:
            the class name / type of the plugin that was not found
        """
        super(PluginNotSupportedError, self).__init__()
        self._message = message
        self._plugin_name = plugin_name

    def __str__(self):
        return self._message

    @property
    def message(self):
        """Descriptive message for the error"""
        return self._message

    @property
    def plugin_name(self):
        """Name of the unsupported plugin"""
        return self._plugin_name


if __name__ == "__main__":  # pragma: no cover
    pass
