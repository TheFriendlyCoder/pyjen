.. PyJen documentation master file, created by
   sphinx-quickstart on Thu Nov  6 22:18:24 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyJen - Jenkins CI Python library
=================================

.. image:: https://img.shields.io/pypi/l/pyjen.svg
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pyjen.svg
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Python Versions

.. image:: https://img.shields.io/pypi/dm/pyjen.svg
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/format/pyjen.svg
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Format

.. image:: https://badge.fury.io/py/pyjen.svg
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Latest Version

.. image:: https://api.travis-ci.org/TheFriendlyCoder/pyjen.svg?branch=master
    :target: https://travis-ci.org/TheFriendlyCoder/pyjen
    :alt: Build status


Table of Contents
=================
.. toctree::
   :maxdepth: 1

   examples
   contrib_guide
   API Docs <api/modules>
   revision_history
   faq

Overview
=============

PyJen is an extensible, user and developer friendly Python interface to the `Jenkins <http://jenkins-ci.org/>`_ CI tool, wrapping the features exposed by the standard REST `API <https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API/>`_ using Pythonic objects and functions. Tested against the latest 2.x and 3.x versions of CPython and the latest trunk and LTS editions of the Jenkins REST API, we endeavor to provide a stable, reliable tool for a variety of users.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins, including views, jobs and builds are easily accessible and can be loaded, analyzed and even modified or created via simple Python commands.

Comments, suggestions and bugs may be reported to the project `maintainer <mailto:kevin@thefriendlycoder.com>`_

Quick Start Guide
=================

1. First, and most obviously, you must have Python installed on your system. For details specific to your OS we recommend seeing `Python's website <http://www.python.com/>`_. We recommend using the latest version of Python 2.x / 3.x for best results.

2. Next, we recommend that you install the pip package manager as described `here <http://www.pip-installer.org/en/latest/installing.html>`_. If you are using newer editions of Python (3.x), or if you are using certain Linux distributions / packages you likely already have this tool installed. You can confirm this by running the following command:

::

    # pip --version

which should result in output that looks something like this:

::

    pip 8.0.2 from C:\Python34x64\lib\site-packages (python 3.4)

3. Install PyJen directly from PyPI using PIP:

::

    # pip install pyjen

4. import the pyjen module and start scripting! Here is a short example that shows how you can get the name of the default view from a Jenkins instance:
::

    >>> from pyjen.jenkins import Jenkins
    >>> jenkins_obj = Jenkins("http://localhost:8080", ('username', 'passwd'))
    >>> default_view = jenkins_obj.default_view
    >>> print(default_view.name)


