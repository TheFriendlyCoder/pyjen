.. This is a readme file encoded in reStructuredText format, intended for use on the summary page for the pyjen
.. PyPI project. Care should be taken to make sure the encoding is compatible with PyPI's markup
.. syntax. See this site for details:
.. http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
..

=============
Overview
=============
.. image:: https://pypip.in/download/pyjen/badge.png
    :target: https://pypi.python.org/pypi//pyjen/
    :alt: Downloads
    
.. image:: https://pypip.in/license/pyjen/badge.png
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: License
    
.. image:: https://pypip.in/wheel/pyjen/badge.png
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Wheel Status
    
.. image:: https://pypip.in/version/pyjen/badge.png
    :target: https://pypi.python.org/pypi/pyjen/
    :alt: Latest Version
    
Extensible, user and developer friendly Python interface to the `Jenkins <http://jenkins-ci.org/>`_ CI tool, wrapping
the features exposed by the standard REST `API <https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API/>`_ using
Pythonic objects and functions. Tested against the latest 2.x and 3.x versions of Python, and the
latest trunk and LTS editions of Jenkins.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming
language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins,
including views, jobs and builds are easily accessible and can be loaded, analyzed and even modified or created
via simple Python commands.

Comments, suggestions and bugs may be reported to the project `maintainer <mailto:kevin@thefriendlycoder.com>`_

Full API documentation can be found at `TheFriendlyCoder.com <http://www.thefriendlycoder.com/PyJen>`_.

=================
Quick start guide
=================
1. First, we recommend that you install the pip package manager as described `here <http://www.pip-installer.org/en/latest/installing.html>`_

2. Install PyJen directly from PyPI using PIP: 

:: 

# pip install pyjen --pre

3. import the pyjen module and start scripting! See below for some common examples.

================
Examples
================
Display a list of all jobs on the default view
------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jk = Jenkins.easy_connect("http://localhost:8080")
    vw = jk.get_default_view()
    jobs = vw.get_jobs()

    for j in jobs:
        print j.get_name()
        

Disable all jobs in a view named "My View"
---------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jk = Jenkins.easy_connect("http://localhost:8080")
    vw = jk.find_view("My View")
    vw.disable_all_jobs()
    

Get all upstream dependencies of a job named "JobA"
------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jen = Jenkins.easy_connect("http://localhost:8080")
    jb = jen.find_job("JobA")
    upstream = jb.get_upstream_jobs(True)

    for u in upstream:
        print u.get_name()

Clone all jobs in a view who are named with a 'trunk' identifier for a new branch configuration
------------------------------------------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    j = Jenkins.easy_connect("http://localhost:8080")
    v = j.find_view("trunk_builds")
    v.clone_all_jobs(".*trunk.*", "branch")