class PyJenError (Exception):
    """Base class for all PyJen related exceptions"""
    pass

class InvalidUserParamsError (PyJenError):
    """Exception caused by invalid parameters in the user configuration file"""
    def __init__(self, msg, file):
        """constructor
        
        :param str msg: Descriptive message associated with this exception
        :param str file: Config file being parsed that causd the exception
        """
        self.__msg = msg
        self.__file = file
        
    def __str__(self):
        return ("Error processing log file: " + self.__file + "\n\t" + self.__msg)
        
class InvalidJenkinsURLError (PyJenError):
    """Exception raised when attempting to connect to a URL that doesn't point to a valid Jenkins REST API"""
    def __init__ (self, msg, url):
        """constructor
        
        :param str msg: Descriptive message associated with this exception
        :param str url: URL in question that does not point to a valid Jenkins REST API
        """
        self.__msg = msg
        self.__url = url
        
    def __str__ (self):
        return "Error connecting to Jenkins API via " + self.__url + ": \n\t" + self.__msg

class InvalidParameterError(PyJenError):
    """Exception raised when the caller provides an invalid value as an input parameter to a PyJen method call"""
    def __init__ (self, msg):
        """Constructor
        
        :param str msg: Descriptive message associated with this exception
        """
        self.__msg = msg
        
    def __str__(self):
        return self.__msg
if __name__ == "__main__":
    pass