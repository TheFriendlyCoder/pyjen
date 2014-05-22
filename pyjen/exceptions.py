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
        self.msg = msg
        self.file = file
        
    def __str__(self):
        return ("Error processing log file: " + self.file + "\n\t" + self.msg)
        
        
if __name__ == "__main__":
    pass