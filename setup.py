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

    Args:
        project (str):
            the name of the current project. It is also assumed that the project
            sources will be located under a sub-folder of the same name.

    Returns:
        list (str):
            shell scripts exposed by this project. Produces an empty
            list if there are no shell scripts supported by the project.
    """
    scripts_path = os.path.join('src', project, 'scripts')
    if not os.path.exists(scripts_path):
        return []

    scripts_namespace = f"{project}.scripts"
    retval = []

    py_scripts = os.listdir(scripts_path)
    for py_file in py_scripts:
        file_parts = os.path.splitext(py_file)
        if file_parts[1] == ".py" and file_parts[0] != '__init__':
            script_config = \
                f"{file_parts[0]}={scripts_namespace}.{file_parts[0]}:main"
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

    Args:
        project (str):
            the name of the current project. It is also assumed that the project
            sources will be located under a sub-folder of the same name.

    Returns:
        list (str):
            list of plugins exposed by this project. Produces an empty
            list if there are no plugins supported by the project.
    """
    plugins_path = os.path.join('src', project, 'plugins')
    if not os.path.exists(plugins_path):
        return []

    plugins_namespace = f"{project}.plugins"
    retval = []

    py_scripts = os.listdir(plugins_path)
    for py_file in py_scripts:
        file_parts = os.path.splitext(py_file)
        if file_parts[1] == ".py" and file_parts[0] != '__init__':
            script_config = \
                f"{file_parts[0]}={plugins_namespace}.{file_parts[0]}:" \
                f"PluginClass"
            retval.append(script_config)

    return retval


def _verify_src_version(version):
    """Checks to make sure an arbitrary character string is a valid version id

    Version numbers are expected to be of the form X.Y.Z

    Args:
        version (str): string to validate

    Returns:
        bool: True if the string is a version number, else false
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

    Args:
        project (str): the name of the project to get the version for

    Returns:
        str: the version for the specified project
    """
    root_dir = os.path.dirname(__file__)
    ver_path = os.path.join(root_dir, 'src', project, 'version.py')
    assert os.path.exists(ver_path)

    with open(ver_path, encoding="utf-8") as prop_file:
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
    """Retrieves the version number for a project

    Args:
        project (str):
            the name of the project being built

    Returns:
        str:
            version number for the project, accounting for an pre-release
            suffixes that may be needed
    """

    retval = _src_version(project)

    if 'TRAVIS_TAG' in os.environ and not os.environ['TRAVIS_TAG'] == '':
        # HACK: Let us assume we're going to use the tag name
        #       when building the template project. Makes it
        #       easier to test release builds
        if project == "ksp_sample":
            return os.environ['TRAVIS_TAG']

        # make sure the tag name matches our version number
        if not os.environ['TRAVIS_TAG'] == retval:
            raise Exception(f"Tag {os.environ['TRAVIS_TAG']} is "
                            f"expected to be {retval}")
        # If we build from a tag, just use the version number verbatim
        return retval

    # Pre release versions need a non-numeric suffix on the version number
    retval += ".dev"
    if 'TRAVIS_BUILD_NUMBER' in os.environ:
        retval += os.environ['TRAVIS_BUILD_NUMBER']
    elif 'GITHUB_RUN_ID' in os.environ:
        retval += os.environ['GITHUB_RUN_ID']
    else:
        retval += "0"

    return retval


def generate_readme(project, repo=None, version=None):
    """Generates a readme for the Python package, based on the readme file

    Args:
        project (str):
            name of the project to generate the readme for
        repo (str):
            optional name of the git repo for the project
            if not provided, it is assumed the repo name matches the project
            name
        version (str):
            optional version of the package being generated
            when not provided, will default to "latest"

    Returns:
        str: readme text for the package
    """
    if repo is None:
        repo = project

    if not version or "dev" in version:
        branch = "branch=master"
        version = "latest"

    else:
        branch = "tag=" + version

    headers = []
    headers.append({
        "image":
            f"https://travis-ci.org/TheFriendlyCoder/{repo}.svg?{branch}",
        "target":
            f"https://travis-ci.org/TheFriendlyCoder/{repo}",
        "text": "Build Automation"
    })
    headers.append({
        "image": f"https://coveralls.io/repos/github/TheFriendlyCoder/{repo}/"
                 f"badge.svg?{branch}",
        "target":
            f"https://coveralls.io/github/TheFriendlyCoder/{repo}?{branch}",
        "text": "Test Coverage"
    })
    headers.append({
        "image":
            f"https://img.shields.io/pypi/pyversions/{project}.svg",
        "target": f"https://pypi.python.org/pypi/{project}",
        "text": "Python Versions"
    })
    headers.append({
        "image": f"https://readthedocs.org/projects/{project}/badge/"
                 f"?version={version}",
        "target": f"http://{project}.readthedocs.io/en/{version}",
        "text": "Documentation Status"
    })
    headers.append({
        "image":
            f"https://requires.io/github/TheFriendlyCoder/{repo}/"
            f"requirements.svg?{branch}",
        "target":
            f"https://requires.io/github/TheFriendlyCoder/{repo}/"
            f"requirements/?{branch}",
        "text": "Requirements Status"
    })
    headers.append({
        "image": f"https://img.shields.io/pypi/format/{project}.svg",
        "target": f"https://pypi.python.org/pypi/{project}/",
        "text": "Package Format"
    })
    headers.append({
        "image": f"https://img.shields.io/pypi/dm/{project}.svg",
        "target": f"https://pypi.python.org/pypi/{project}/",
        "text": "Download Count"
    })
    headers.append({
        "image": f"https://img.shields.io/pypi/l/{project}.svg",
        "target": "https://www.apache.org/licenses/LICENSE-2.0.txt",
        "text": "Apache License 2.0"
    })

    retval = ""
    for cur_header in headers:
        retval += f""".. image:: {cur_header["image"]}
    :target: {cur_header["target"]}
    :alt: {cur_header["text"]}

    """
        retval += "\n"

    with open('README.rst', encoding="utf-8") as readme:
        retval += readme.read()

    return retval


def load_project_properties():
    """
    Returns:
        dict: project specific properties from the project.prop file
    """
    src_path = os.path.dirname(__file__)
    filename = os.path.join(src_path, 'project.prop')
    with open(filename, encoding="utf-8") as prop_file:
        props = prop_file.read()
    return ast.literal_eval(props)


def main():
    """main entrypoint function"""
    PROJECT["VERSION"] = get_version_number(PROJECT["NAME"])
    _plugin_namespace = f"{PROJECT['NAME']}.plugins.v{PROJECT['PLUGIN_VER']}"
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
        url=f'https://github.com/TheFriendlyCoder/{PROJECT["NAME"]}',
        keywords=PROJECT["KEYWORDS"],
        entry_points={
            _plugin_namespace: load_plugins(PROJECT["NAME"]),
            'console_scripts': load_console_scripts(PROJECT["NAME"]),
        },
        install_requires=PROJECT["DEPENDENCIES"],
        python_requires=PROJECT["SUPPORTED_PYTHON_VERSION"],
        extras_require={
            'dev': PROJECT["DEV_DEPENDENCIES"],
        },
        license="Apache License 2.0",
        # https://pypi.org/classifiers/
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "License :: OSI Approved :: Apache Software License",
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
