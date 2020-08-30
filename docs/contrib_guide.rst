Contributors Guide
==================

Developers who are interested in contributing to the PyJen project should start
by contacting the project maintainer
`here <mailto:thefriendlycoder@gmail.com>`_. Source for the project can be
found on `GitHub <https://github.com/TheFriendlyCoder/pyjen>`_.

To start working on an improvement for the project, start by forking the
project and committing your work there. When you are happy with the changes
you have made create a pull request and assign it to the maintainer. Once
approved, the changes will be integrated into the next release.

All code is expected to be PEP-8 compliant. This requirement is enforced
automatically by our continuous integration builds with the help of PyLint.
Pull requests will not be approved when continuous integration builds fail.
Further, we ask that all docstrings be compatible with the Sphinx API-doc plugin
to facilitate automatic document generation by our scripts and hosting sites.
Finally, we encourage contributors to add sufficient unit test coverage for
any changes they make using the py.test framework used by this project.

Seeing as how PyJen supports the latest versions of both Python 2 and Python 3,
all code contributions must be compatible with both of these versions. Finally,
we try our best to ensure the API is compatible with both the LTS
and Latest editions of the Jenkins REST API, so care should be taken to make
sure contributed code - especially those supporting new Jenkins plugins -
is compatible with both of these versions wherever possible.

=======================
Development Environment
=======================

The project, including all build tools, are expected to work correctly on all
major operating systems (Windows, Linux, MacOS) and under all recent versions
of Python (2.7, 3.4+). Further, some unit tests require the Docker client tools
to be installed as well. See the section on "testing" below for details.

Once you have your host configured correctly, we recommend using a Python
virtual environment for all of your development work. Maintainers of the project
are currently using `virtualenv <https://virtualenv.pypa.io/en/latest/>`_
however any similar virtualization tool should work. Below are the basic
steps we recommend contributors follow to set up a compatible build environment:

1. make sure you have the 'virtualenv' tool installed

::

    pip install virtualenv


2. Next, create a local virtual environment under your working folder for the
   desired Python version. In most systems this can be done as follows:

::

    virtualenv -p python3 ./venv3


3. Activate the new virtual environment

::

    Linux/Mac: source ./venv3/bin/activate
    Windows: .\venv3\bin\activate.bat

4. install the required build time dependencies. There are 2 requirements files
   in the ./tests folder to simplify this process: python2.reqs and
   python3.reqs. The former defines all pegged revisions of all dependencies
   needed to build and test the project under a Python 2 runtime. The latter
   defines a similar set of dependencies for the Python 3 runtime. These can
   easily be installed using pip as follows:

::

    pip install -r ./tests/python3.reqs

5. Finally, you should be ready to try performing a test run of the unit tests.

::

    tox -r -e py3

For more details on different aspects of the project, including more details on
how the test framework works, dependency management, as well as some high level
architectural information to get you started writing plugins, see the other
sections below.


=======
Testing
=======

We endeavor to have as much test coverage of the library and plugin code as
possible. To help simplify testing and improve coverage metrics we've adopted
several different testing strategies.

Currently, all tests are orchestrated by
`tox <https://tox.readthedocs.io/en/latest/>`_. Under the hood tox runs static
code analysis as well as automated unit tests. The tests are further
orchestrated using `pytest <https://docs.pytest.org/en/latest/>`_. Further,
some tests in the suite require a live Jenkins service to test against. This
service is automatically created and configured by the pytest framework. To
run these tests you need only install the
`Docker client <https://www.docker.com>`_ for your development system and make
sure the service is running before launching tox.

For examples on how to write tests for various parts of the framework and
plugins, we encourage you to review the existing tests and find similar ones
that you can use as guides. Simply copy a test that performs a similar operation
to what you want to test, rename the test and update the implementation to
satisfy your new test case.

-------------------
Test Customizations
-------------------

Several custom pytest parameters have been added to our test runner to make
working with the project easier for contributors. They are as follows:

::

    tox -e py3 -- --skip-docker

This handy flag allows developers to run the unit tests that do not depend
on the Jenkins service that runs under Docker. This can be helpful for
contributors who can't or don't want to install and configure Docker on their
local machines. Also, tests that require the Docker service tend to be slower
than their non-dockerized counterparts, so it can be helpful to run the faster
tests as an initial sanity check for new changes being made.

::

    tox -e py3 -- --preserve

This flag forces the pytest runner to keep the Docker container used for tests
running after the test run is complete. This can be handy for debugging purposes
allowing developers to examine the contents of the container after the tests
have been executed to see what state the service is in, the state of the file
system in the container, etc. Also, when this flag is enabled subsequent runs
of the tests will re-use the same container, which can help improve build times
when doing local testing.

::

    tox -e py3 -- --jenkins-version jenkins:alpine

This test option allows us to customize the version of the Jenkins service we
test against more easily. By providing the name and tag of the Docker image to
use for testing, we can force the test runner to use that exact container for
all tests, superseding the default one. Have a bug with a plugin that is only
reproducible in v2.150.3, then just run
"tox -e py3 -- --jenkins-version jenkins:2.150.3-alpine" to try and reproduce
it.

=====================
Dependency Management
=====================

To ensure consistent build results on all platforms and on all continuous
integrations servers, we peg all of the build time dependencies needed to
build and test the project as specific versions. These pegged revisions are
stored in the following files:

* ./tests/python2.reqs - all dependencies needed to build under Python 2.x
* ./tests/python3.reqs - all dependencies needed to build under Python 3.x

To make it easier to manage these requirements files, we have a custom shell
script in the root folder that will auto-generate a new set of dependencies
for the project based on the package dependencies defined in the project.prop
file in the root of the project. The shell script will update the dependency
list with all of the latest versions of all dependencies automatically.

=======
Plugins
=======
Just as found in the Jenkins back end implementation, most custom functionality
in PyJen will be provided by plugins. PyJen supports a plugin system that
essentially mirrors the Jenkins system which allows developers to write their
own classes to wrap the REST API for any Jenkins plugin they may like.

Plugins may be packaged independently from the PyJen package or included with
the package. Plugins included here are guaranteed to be covered by the same
quality metrics and standards as the main library itself, which should improve
the confidence users have in them. Standalone plugins packaged separately will
be written by third parties and thus may vary greatly in quality and features.

Plugins included directly with the PyJen library are simply Python classes that
meet the following criteria:

* the class declarations must be placed in a module under the src/pyjen/plugins
  subfolder
* the class must derive, directly or indirectly, from the
  :py:class:`~.utils.xml_plugin.XMLPlugin` abstract base class

This second requirement forces derived classes to implement specific criteria
to implement the required abstract interface. Currently this interface simply
has two requirements:

* a static property named 'type' of type :class:`str` containing the character
  representation of the Jenkins plugin managed by the PyJen plugin
* a constructor compatible with the type of plugin being managed
  (in most cases, this is a single parameter of type
  :class:`xml.etree.ElementTree.Element`.)

Beyond that, plugin implementers can then proceed to implement public methods
and properties on their plugin class to expose functionality particular to the
plugin.

-------------
Using Plugins
-------------

Any primitive or operation in Jenkins that supports a plugable interface is
equally addressable by the associated PyJen interface without further
customization by the plugin author. For example, to add support for a new type
of 'builder', simply write your plugin class as described above and it will
automatically be accessible from the
:py:meth:`~.pyjen.plugins.freestylejob.FreestyleJob.builders`
property.

This is accomplished by leveraging the metadata embedded in the Jenkins
configuration information for each primitive such as a view or a job. The
back-end Java plugins supported by Jenkins embed type information in the
configuration metadata which maps directly onto PyJen plugin classes. So when
you use PyJen to request data from the Jenkins REST API it will automatically
look for and load any plugin that the active Jenkins instance may be using
without further modification to the PyJen API.

