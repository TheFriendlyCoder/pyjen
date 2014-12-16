Contributors Guide
==================

Developers who are interested in contributing to the PyJen project should start by contacting the project
maintainer `here <mailto:kevin@thefriendlycoder.com>`_. Source for the project can be found on GitHub
`here <https://github.com/TheFriendlyCoder/pyjen>`_.

To start working on an improvement for the project, start by creating a development branch and committing your
work there. When you are happy with the changes you have made simply perform a pull request.

We try to keep our code inline with PEP-8 standards, and we do have PyLint support in the project to verifying
the content meets this standard. Further, we ask that all docstrings be compatible with the Sphinx API-doc plugin
to facilitate automatic document generation by our scripts and hosting sites.

=======
Plugins
=======
Just as found in the Jenkins back end implementation, most custom functionality in PyJen will be provided by plugins.
PyJen supports a plugin system that essentially mirrors the Jenkins system which allows developers to write their own
classes to wrap the REST API for any plugin they may like.

At the most basic level, PyJen plugins are simply Python classes that meet the following two criteria:

* the class declarations must be placed in a module under the pyjen/plugins subfolder
* the class must derive, directly or indirectly, from te :py:class:`~.utils.plugin_base.PluginBase` abstract base class

This second requirement forces derived classes to implement specific criteria to implement the required abstract
interface. Currently this interface simply has two requirements:

* a static property named 'type' of type :class:`str` containing the character representation of the Jenkins plugin
  managed by the PyJen plugin
* a constructor compatible with the type of plugin being managed (in most cases, this is a single parameter of type
  :class:`xml.ElementTree.Element`.)

Beyond that, plugin implementers can then proceed to implement public methods and properties on their plugin class
to expose functionality particular to the plugin.

-------------
Using Plugins
-------------

Any primitive or operation in Jenkins that supports a plugable interface is equally addressable by the associated
PyJen interface without further customization by the plugin author. For example, to add support for a new type of
'builder', simply write your plugin class as described above and it will automatically be accessible from the
:py:meth:`~.pyjen.job.Job.builders` property.
