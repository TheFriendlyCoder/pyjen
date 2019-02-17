"""
Abstraction layer for the Jenkins REST API designed to simplify the interaction
with the Jenkins web interface from the Python scripting environment.
"""
import logging
import ast
import pkg_resources

__version__ = ast.literal_eval(
    pkg_resources.resource_string(__name__, "version.prop").decode("utf-8")
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
