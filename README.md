<!---
This is a readme file encoded in markdown format, intended for use on the summary page for the pyjen
github project. Care should be taken to make sure the encoding is compatible with github's markdown
syntax. See this site for details:
http://daringfireball.net/projects/markdown/syntax
-->

Overview
============
Extensible, user and developer friendly Python interface to the [Jenkins CI](http://jenkins-ci.org/) tool, wrapping
the features exposed by the standard [REST API](https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API) in a 
Pythonic objects and functions. Tested against the latest 2.x and 3.x versions of Python, and the
latest trunk and LTS editions of Jenkins.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming
language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins,
including views, jobs and builds are easily accessible and can be accessed, analyzed and even modified or created
via simple Python commands.

Comments, suggestions and bugs may be reported to the project [maintainer](mailto:kevin@thefriendlycoder.com).

Full API documentation can be found at [TheFriendlyCoder.com](http://www.thefriendlycoder.com/PyJen)

Quick start guide
=================
1. First, we recommend that you install the pip package manager as described on the [pip](http://www.pip-installer.org/en/latest/installing.html) website.

2. Install PyJen directly from PyPI using PIP: 

    > pip install pyjen

3. By default the PyJen API supports connecting to an unsecured locally hosted instance of Jenkins. To
enable support for remote servers and authentication you will need to create a configuration file file
named '.pyjen' in your home folder:

    Windows:
    > notepad %userprofile%\.pyjen
    
    Linux:
    > vi ~/.pyjen

4. To enable remote connections add the following lines to your config file:

    > [jenkins_config]
    > url=http://MyServer/jenkins/

5. To enable authenticated connections to this Jenkins instance add the following lines to the config file:

    > [credentials]
    > username=MyUser
    > password=MyPassword!

6. Import pyjen into your project and start scripting!

Examples
====================
Display a list of all jobs on the default view
-----------------------------------------------
    from pyjen import *
    jk = jenkins("http://localhost:8080")
    vw = jk.get_default_view()
    jobs = vw.get_jobs()
    
    for j in jobs:
        print j.get_name()
        
Disable all jobs in a view named "My View"
---------------------------------------------
    from pyjen import *
    jk = jenkins("http://localhost:8080")
    vw = jk.find_view("My View")
    vw.disable_all_jobs()
    
Get all upstream dependencies of a job named "JobA"
-----------------------------------------------------
    from pyjen import *
    j = job("http://localhost:8080/job/JobA")
    upstream = j.get_upstream_jobs(True)
    
    for u in upstream:
        print u.get_name()

Clone all jobs in a view who are named with a 'trunk' identifier for a new branch configuration
------------------------------------------------------------------------------------------------
    from pyjen import *
    v = view("http://localhost:8080/views/trunk_builds")
    v.clone_all_jobs(".*trunk.*", "branch")
