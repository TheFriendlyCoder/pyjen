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
    scripts_path = os.path.join('src', project, 'scripts')
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


def load_plugins(project):
    """Generates list of plugins for use by Python setup tools

    Each element in this list defines the name and entry point function for each
    plugin included with the current project.

    This script assumes that any python script found in a folder named 'plugins'
    under the project folder is to be registered as an extension point for
    the library.

    The output from this function can be provided to the setuptools.setup()
    function, something like this:

    entry_points={
        PROJECT["NAME"] + ".plugins" : load_plugins(project_name)
    }

    :param str project:
        the name of the current project. It is also assumed that the project
        sources will be located under a sub-folder of the same name.
    :return:
        list of plugins exposed by this project. Produces an empty
        list if there are no plugins supported by the project.
    """
    plugins_path = os.path.join('src', project, 'plugins')
    if not os.path.exists(plugins_path):
        return []

    plugins_namespace = "{0}.plugins".format(project)
    retval = []

    py_scripts = os.listdir(plugins_path)
    for py_file in py_scripts:
        file_parts = os.path.splitext(py_file)
        if file_parts[1] == ".py" and file_parts[0] != '__init__':
            script_config = "{0}={1}.{0}:PluginClass".format(
                file_parts[0],
                plugins_namespace
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
    root_dir = os.path.dirname(__file__)
    ver_path = os.path.join(root_dir, 'src', project, 'version.py')
    assert os.path.exists(ver_path)

    with open(ver_path) as prop_file:
        data = ast.parse(prop_file.read())

    # The version.py file is expected to contain only a single statement
    # of the form:
    #       __version__ = "1.2.3"
    assert len(data.body) == 1
    statement = data.body[0]
    assert isinstance(statement, ast.Assign)
    assert len(statement.targets) == 1
    assert statement.targets[0].id == "__version__"
    assert isinstance(statement.value, ast.Str)

    # If we get here we know the one statement in the version module has
    # a string value with the version number in it, so we just return it here
    return statement.value.s


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

    with open('README.rst') as readme:
        retval += readme.read()

    return retval


def load_project_properties():
    """Loads project specific properties from the project.prop file

    :returns: project properties
    :rtype: :class:`dict`
    """
    src_path = os.path.dirname(__file__)
    with open(os.path.join(src_path, 'project.prop')) as prop_file:
        props = prop_file.read()
    return ast.literal_eval(props)


def main():
    """main entrypoint function"""
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
            PROJECT["NAME"] + ".plugins" : load_plugins(PROJECT["NAME"]),
            'console_scripts': load_console_scripts(PROJECT["NAME"]),
        },
        install_requires=PROJECT["DEPENDENCIES"],
        python_requires=PROJECT["SUPPORTED_PYTHON_VERSION"],
        extras_require={
            'dev': PROJECT["DEV_DEPENDENCIES"],
        },
        # The following support files are needed by this setup.py script
        # These files are not deployed with the project when building a wheel
        # file, and thus are only used by sdist builds. In turn, these are
        # required by tox to run unit tests because tox does not currently
        # support running tests from a dynamically generated wheel file.
        data_files=[
            ("", [
                "project.prop",
                ]
            ),
        ],
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


if __name__ == "__main__":
    PROJECT = load_project_properties()
    main()
