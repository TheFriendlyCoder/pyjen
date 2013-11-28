"""
Abstraction layer for the Jenkins REST API designed to simplify
the interaction with the Jenkins web interface from the Python
scripting environment.
"""

# first import all key Jenkins classes from package
from .jenkins import jenkins
from .build import build
from .job import job
from .node import node
from .view import view

#Then, lets expose these classes to the caller when they import *
__all__ = ["jenkins", "view", "node", "build", "job"]
