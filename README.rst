=============
Overview
=============

Extensible, user and developer friendly Python interface to the `Jenkins <http://jenkins-ci.org/>`_ CI tool, wrapping
the features exposed by the standard REST `API <https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API/>`_ using
Pythonic objects and functions. Tested against the latest 2.x and 3.x versions of Python, and the
latest trunk and LTS editions of Jenkins.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming
language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins,
including views, jobs and builds are easily accessible and can be loaded, analyzed and even modified or created
via simple Python commands.

Comments, suggestions and bugs may be reported to the project `maintainer <mailto:kevin@thefriendlycoder.com>`_

Full API documentation can be found on `ReadTheDocs.org <http://pyjen.readthedocs.org/en/v0.0.10dev/>`_.

=================
Quick start guide
=================
1. First, we recommend that you install the pip package manager as described `here <http://www.pip-installer.org/en/latest/installing.html>`_

2. Install PyJen directly from PyPI using PIP:

::

# pip install pyjen --pre

3. import the pyjen module and start scripting! See below for some common examples.

For a more in-depth guide to contributing to the project, see our
`contributors guide <https://pyjen.readthedocs.org/en/v0.0.10dev/contrib_guide.html>`_.

================
Examples
================
Display a list of all jobs on the default view
------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jk = Jenkins("http://localhost:8080")
    vw = jk.default_view
    jobs = vw.jobs

    for j in jobs:
        print(j.name)


Disable all jobs in a view named "My View"
---------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jk = Jenkins("http://localhost:8080")
    vw = jk.find_view("My View")
    vw.disable_all_jobs()


Get all upstream dependencies of a job named "JobA"
------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jen = Jenkins("http://localhost:8080")
    jb = jen.find_job("JobA")
    upstream = jb.all_upstream_jobs

    for u in upstream:
        print(u.name)

Clone all jobs in a view who are named with a 'trunk' identifier for a new branch configuration
------------------------------------------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    j = Jenkins("http://localhost:8080")
    v = j.find_view("trunk_builds")
    v.clone_all_jobs("trunk", "branch")
