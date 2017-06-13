#!/usr/bin/env python
from setuptools import setup, find_packages
import os
from distutils.util import convert_path

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# project specific parameters
# coverage<4 - needed in python 3.2 development environments
project_name = 'pyjen'
project_dependencies = ['requests[security]>=2.0.1', 'six', 'tqdm']
project_dev_dependencies = ['wheel', 'twine', 'pytest', 'pytest-cov', 'mock', 'radon', 'pylint', 'sphinx>=1.2.3', 'tox']
project_description = 'Python wrapper for the Jenkins CI REST API'
project_keywords = 'jenkins jenkins-ci api wrapper library'
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def load_console_scripts(project):
    """Generates list of 'entry point' functions for use by Python setup tools

    Each element in this list defines the name and entry point function for each
    python script included with the current project that is to be exposed to
    user's shells when the package is installed.

    This script assumes that any python script found in a folder named 'scripts'
    under the project folder is to be exposed on the shell during deployment.
    Further, this script assumes that all such scripts expose a public function
    called 'main' which will act as the primary entry point for the script. This
    function will then be responsible for parsing any supported command line parameters
    and executing the appropriate functionality.

    The output from this function can be provided to the setuptools.setup() function,
    something like this:

    entry_points={
        'console_scripts': load_console_scripts(project_name)
    }

    :param str project: the name of the current project. It is also assumed that
                        the project sources will be located under a sub-folder
                        of the same name.
    :return: list of shell scripts exposed by this project. Produces an empty list if
             there are no shell scripts supported by the project.
    """
    scripts_path = os.path.join(project, 'scripts')
    if not os.path.exists(scripts_path):
        return []

    scripts_namespace = "{0}.scripts".format(project)
    retval = []

    py_scripts = os.listdir(scripts_path)
    for py_file in py_scripts:
        file_parts = os.path.splitext(py_file)
        if file_parts[1] == ".py" and file_parts[0] != '__init__':
            script_config = "{0}={1}.{0}:main".format(file_parts[0], scripts_namespace)
            retval.append(script_config)

    return retval


def check_tag_name(tag_name):
    """Ensures the name of the current SCM tag is correctly formatted

    Tag should represent a version number of the form X.Y.Z
    
    :returns: True if the tag name satisfies the expected format, false if not
    """

    parts = tag_name.split(".")
    if len(parts) != 3:
        return False

    for cur_digit in parts:
        if not cur_digit.isdigit():
            return False

    return True


def get_version_number():
    """Retrieves the version number for a project"""

    # If we are building from a tag using Travis-CI, set our version number to the tag name
    if 'TRAVIS_TAG' in os.environ and not os.environ['TRAVIS_TAG'] == '':
        if not check_tag_name(os.environ['TRAVIS_TAG']):
            raise Exception("Invalid tag name {0}. Must be of the form 'X.Y.Z'".format(os.environ['TRAVIS_TAG']))
        return os.environ['TRAVIS_TAG']

    # if we get here we know we're building a pre-release version
    # so we set a fake version as a place holder
    retval = "0.0"

    # If we are building from a branch using Travis-CI, append the build number so we know where the
    # package came from
    if 'TRAVIS_BUILD_NUMBER' in os.environ:
        retval += "." + os.environ['TRAVIS_BUILD_NUMBER']
    else:
        retval += ".0"

    # Pre release versions need a non-numeric suffix on the version number
    retval += ".dev0"

    return retval

project_packages = find_packages()


# Execute packaging logic
setup(
    name=project_name,
    version=get_version_number(),
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    packages=project_packages,
    description=project_description,
    long_description=open('README.rst').read(),
    url='https://github.com/TheFriendlyCoder/' + project_name,
    keywords=project_keywords,
    entry_points={
        'console_scripts': load_console_scripts(project_name),
        'pyjen.plugins': [
            'subversion=pyjen.plugins.subversion:Subversion'
        ]
    },
    install_requires=project_dependencies,
    extras_require={
        'dev': project_dev_dependencies
    },
    license="GPL",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries"
    ]
)
