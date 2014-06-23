"""
Abstraction layer for the Jenkins REST API designed to simplify
the interaction with the Jenkins web interface from the Python
scripting environment.
"""

# first import all key Jenkins classes from package
from pyjen.jenkins import jenkins
from pyjen.build import build
from pyjen.job import job
from pyjen.node import Node
from pyjen.view import view

#Then, lets expose these classes to the caller when they import *
__all__ = ["jenkins", "view", "Node", "build", "job"]
