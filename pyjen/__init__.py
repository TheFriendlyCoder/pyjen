"""
Abstraction layer for the Jenkins REST API designed to simplify the interaction with the Jenkins web interface
from the Python scripting environment.
"""
import pkg_resources

__version__ = pkg_resources.get_distribution(__name__).version
