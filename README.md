Extensible, user and developer friendly Python interface to the [Jenkins CI](http://jenkins-ci.org/) tool, wrapping
the features exposed by the standard [REST API](https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API) in a 
Pythonic objects and functions.

With an intuitive and well thought out interface, PyJen offers anyone familiar with the Python programming
language an easy way to manage Jenkins dashboards from a simple command prompt. All core primitives of Jenkins,
including views, jobs and builds are easily accessible and can be accessed, analyzed and even modified or created
via simple Python commands.

# Example: Displaying a list of all jobs on the default view
    from pyjen import *
    jk = jenkins("http://localhost:8080")
    vw = jk.get_default_view()
    jobs = vw.get_jobs()
    
    for j in jobs:
    	print j.get_name()
    	