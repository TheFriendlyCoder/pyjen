"""
Abstraction layer for the Jenkins REST API designed to simplify
the interaction with the Jenkins web interface from the Python
scripting environment.
"""

# first import all key Jenkins classes from package
from pyjen.jenkins import Jenkins
from pyjen.build import Build
from pyjen.job import Job
from pyjen.node import Node
from pyjen.view import View

VERSION="0.0.8dev"

#Then, lets expose these classes to the caller when they import *
__all__ = ["Jenkins", "View", "Node", "Build", "Job"]
