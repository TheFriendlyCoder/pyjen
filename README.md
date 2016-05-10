<!---
This is a readme file encoded in markdown format, intended for use on the summary page for the pyjen
github project. Care should be taken to make sure the encoding is compatible with github's markdown
syntax. See this site for details:
http://daringfireball.net/projects/markdown/syntax
-->

Overview
============
[![License](https://img.shields.io/pypi/l/pyjen.svg)](https://pypi.python.org/pypi/pyjen/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyjen.svg)](https://pypi.python.org/pypi/pyjen/)
[![Downloads](https://img.shields.io/pypi/dm/pyjen.svg)](https://pypi.python.org/pypi/pyjen/)
[![Format](https://img.shields.io/pypi/format/pyjen.svg)](https://pypi.python.org/pypi/pyjen/)
[![Latest version](https://badge.fury.io/py/pyjen.svg)](https://badge.fury.io/py/pyjen)
[![Build Status](https://api.travis-ci.org/TheFriendlyCoder/pyjen.svg?branch=master)](https://pypi.python.org/pypi/pyjen/)

Extensible, user and developer friendly Python interface to the [Jenkins CI](http://jenkins-ci.org/) tool, wrapping
the features exposed by the standard [REST API](https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API) in a 
Pythonic objects and functions. Tested against the latest 2.x and 3.x versions of Python, and the
latest trunk and LTS editions of Jenkins.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming
language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins,
including views, jobs and builds are easily accessible and can be accessed, analyzed and even modified or created
via simple Python commands.

Comments, suggestions and bugs may be reported to the project [maintainer](mailto:kevin@thefriendlycoder.com).

Full API documentation can be found at [ReadTheDocs.org](http://pyjen.readthedocs.org/en/latest/)

Quick start guide
=================
1. First, we recommend that you install the pip package manager as described on the [pip](http://www.pip-installer.org/en/latest/installing.html) website.

2. Install PyJen directly from PyPI using PIP: 

    > pip install pyjen --pre

3. import the pyjen module and start scripting! See below for some common examples.

For a more in-depth guide to contributing to the project, see our contributors guide on [ReadTheDocs.com](https://pyjen.readthedocs.org/en/latest/)

Examples
====================
Display a list of all jobs on the default view
-----------------------------------------------
    from pyjen.jenkins import Jenkins
    jk = Jenkins.easy_connect("http://localhost:8080")
    vw = jk.default_view
    jobs = vw.jobs
    
    for j in jobs:
        print(j.name)
        
Disable all jobs in a view named "My View"
---------------------------------------------
    from pyjen.jenkins import Jenkins
    jk = Jenkins.easy_connect("http://localhost:8080")
    vw = jk.find_view("My View")
    vw.disable_all_jobs()
    
Get all upstream dependencies of a job named "JobA"
-----------------------------------------------------
    from pyjen.jenkins import Jenkins
    jen = Jenkins.easy_connect("http://localhost:8080")
    jb = jen.find_job("JobA")
    upstream = jb.all_upstream_jobs
    
    for u in upstream:
        print(u.name)

Clone all jobs in a view who are named with a 'trunk' identifier for a new branch configuration
------------------------------------------------------------------------------------------------
    from pyjen.jenkins import Jenkins
    j = Jenkins.easy_connect("http://localhost:8080/")
    v = j.find_view("trunk_builds")
    v.clone_all_jobs("trunk", "branch")
