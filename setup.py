#!/usr/bin/env python
"""Setuptools packaging script for the project"""
import os
import ast
from setuptools import setup, find_packages


def load_console_scripts(project):
    """Generates list of 'entry point' functions for use by Python setup tools

    Each element in this list defines the name and entry point function for each
    python script included with the current project that is to be exposed to
    user's shells when the package is installed.

    This script assumes that any python script found in a folder named 'scripts'
    under the project folder is to be exposed on the shell during deployment.
    Further, this script assumes that all such scripts expose a public function
    called 'main' which will act as the primary entry point for the script. This
    function will then be responsible for parsing any supported command line
    parameters and executing the appropriate functionality.

    The output from this function can be provided to the setuptools.setup()
    function, something like this:

    entry_points={
        'console_scripts': load_console_scripts(project_name)
    }

    :param str project:
        the name of the current project. It is also assumed that the project
        sources will be located under a sub-folder of the same name.
    :return:
        list of shell scripts exposed by this project. Produces an empty
        list if there are no shell scripts supported by the project.
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
            script_config = "{0}={1}.{0}:main".format(
                file_parts[0],
                scripts_namespace
            )
            retval.append(script_config)

    return retval


def _verify_src_version(version):
    """Checks to make sure an arbitrary character string is a valid version id

    Version numbers are expected to be of the form X.Y.Z

    :param str version: string to validate
    :returns: True if the string is a version number, else false
    :rtype: :class:`bool`
    """
    if not isinstance(version, str):
        return False
    if "." not in version:
        return False
    parts = version.split(".")
    if len(parts) != 3:
        return False

    for cur_part in parts:
        if not cur_part.isdigit():
            return False
    return True


def _src_version(project):
    """Parses the version number from the source project

    :param str project: the name of the project to get the version for
    :returns: the version for the specified project
    :rtype: :class:`str`
    """
    ver_path = os.path.join(os.getcwd(), 'src', project, 'version.prop')
    assert os.path.exists(ver_path)

    data = open(ver_path).read()
    retval = ast.literal_eval(data)

    assert retval is not None
    assert _verify_src_version(retval)
    return retval


def get_version_number(project):
    """Retrieves the version number for a project"""

    retval = _src_version(project)

    if 'TRAVIS_TAG' in os.environ and not os.environ['TRAVIS_TAG'] == '':
        # HACK: Let us assume we're going to use the tag name
        #       when building the template project. Makes it
        #       easier to test release builds
        if project == "ksp_sample":
            return os.environ['TRAVIS_TAG']

        # make sure the tag name matches our version number
        if not os.environ['TRAVIS_TAG'] == retval:
            raise Exception("Tag {0} is expected to be {1}".format(
                os.environ['TRAVIS_TAG'],
                retval
            ))
        # If we build from a tag, just use the version number verbatim
        return retval

    # Pre release versions need a non-numeric suffix on the version number
    retval += ".dev"
    if 'TRAVIS_BUILD_NUMBER' in os.environ:
        retval += os.environ['TRAVIS_BUILD_NUMBER']
    else:
        retval += "0"

    return retval


def generate_readme(project, repo=None, version=None):
    """Generates a readme for the Python package, based on the readme file

    :param str project: name of the project to generate the readme for
    :param str repo:
        optional name of the git repo for the project
        if not provided, it is assumed the repo name matches the project name
    :param str version:
        optional version of the package being generated
        when not provided, the "
    :returns: readme text for the package
    :rtype: :class:`str`
    """
    if repo is None:
        repo = project

    if not version or "dev" in version:
        branch = "branch=master"
        version = "latest"

    else:
        branch = "tag=" + version

    headers = list()
    headers.append({
        "image":
            "https://travis-ci.org/TheFriendlyCoder/{0}.svg?{1}".
            format(repo, branch),
        "target":
            "https://travis-ci.org/TheFriendlyCoder/{0}".
            format(repo),
        "text": "Build Automation"
    })
    headers.append({
        "image": "https://coveralls.io/repos/github/TheFriendlyCoder/{0}/"
                 "badge.svg?{1}".format(repo, branch),
        "target":
            "https://coveralls.io/github/TheFriendlyCoder/{0}?{1}".
            format(repo, branch),
        "text": "Test Coverage"
    })
    headers.append({
        "image":
            "https://img.shields.io/pypi/pyversions/{0}.svg".
            format(project),
        "target": "https://pypi.python.org/pypi/{0}".format(project),
        "text": "Python Versions"
    })
    headers.append({
        "image":
            "https://readthedocs.org/projects/{0}/badge/?version={1}".
            format(project, version),
        "target": "http://{0}.readthedocs.io/en/{1}".format(project, version),
        "text": "Documentation Status"
    })
    headers.append({
        "image":
            "https://requires.io/github/TheFriendlyCoder/{0}/"
            "requirements.svg?{1}".format(repo, branch),
        "target":
            "https://requires.io/github/TheFriendlyCoder/{0}/"
            "requirements/?{1}".format(repo, branch),
        "text": "Requirements Status"
    })
    headers.append({
        "image": "https://img.shields.io/pypi/format/{0}.svg".format(project),
        "target": "https://pypi.python.org/pypi/{0}/".format(project),
        "text": "Package Format"
    })
    headers.append({
        "image": "https://img.shields.io/pypi/dm/{0}.svg".format(project),
        "target": "https://pypi.python.org/pypi/{0}/".format(project),
        "text": "Download Count"
    })
    headers.append({
        "image": "https://img.shields.io/pypi/l/{0}.svg".format(project),
        "target": "https://www.gnu.org/licenses/gpl-3.0-standalone.html",
        "text": "GPL License"
    })

    header_template = """.. image:: {0}
    :target: {1}
    :alt: {2}

    """

    retval = ""
    for cur_header in headers:
        retval += header_template.format(
            cur_header["image"], cur_header["target"], cur_header["text"])
        retval += "\n"

    retval += open('README.rst').read()

    return retval


def load_project_properties():
    """Loads project specific properties from the project.prop file

    :returns: project properties
    :rtype: :class:`dict`
    """
    cur_file = os.path.realpath(__file__)
    cur_path = os.path.split(cur_file)[0]
    props = open(os.path.join(cur_path, 'project.prop')).read()
    return ast.literal_eval(props)


PROJECT = load_project_properties()
PROJECT["VERSION"] = get_version_number(PROJECT["NAME"])

# Execute packaging logic
setup(
    name=PROJECT["NAME"],
    version=PROJECT["VERSION"],
    author='Kevin S. Phillips',
    author_email='thefriendlycoder@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description=PROJECT["DESCRIPTION"],
    long_description=
    generate_readme(PROJECT["NAME"], PROJECT["REPO"], PROJECT["VERSION"]),
    url='https://github.com/TheFriendlyCoder/' + PROJECT["NAME"],
    keywords=PROJECT["KEYWORDS"],
    entry_points={
        'console_scripts': load_console_scripts(PROJECT["NAME"])
    },
    install_requires=PROJECT["DEPENDENCIES"],
    python_requires=PROJECT["SUPPORTED_PYTHON_VERSION"],
    extras_require={
        'dev': PROJECT["DEV_DEPENDENCIES"]
    },
    package_data={
        PROJECT["NAME"]: ["version.prop"]
    },
    license="GPL",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Software Development :: Libraries",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ]
)
