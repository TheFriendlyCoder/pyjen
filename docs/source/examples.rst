Examples
==============

.. toctree::
   :maxdepth: 2

Display a list of all jobs on the default view
------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    jk = Jenkins.easy_connect("http://localhost:8080")
    vw = jk.default_view
    jobs = vw.jobs

    for j in jobs:
        print(j.name)


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
    upstream = jb.all_upstream_jobs

    for u in upstream:
        print u.name

Clone all jobs in a view who are named with a 'trunk' identifier for a new branch configuration
------------------------------------------------------------------------------------------------

::

    from pyjen.jenkins import Jenkins
    j = Jenkins.easy_connect("http://localhost:8080")
    v = j.find_view("trunk_builds")
    v.clone_all_jobs("trunk", "branch")
