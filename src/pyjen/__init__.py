"""
Abstraction layer for the Jenkins REST API designed to simplify the interaction
with the Jenkins web interface from the Python scripting environment.
"""
import logging
from .version import __version__

logging.getLogger(__name__).addHandler(logging.NullHandler())
