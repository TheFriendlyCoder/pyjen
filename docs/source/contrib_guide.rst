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
Once the PyJen API is complete, most custom functionality will be provided by plugins. PyJen supports a plugin
system that essentially mirrors the Jenkins plugin system which allows developers to write their own classes
to wrap the REST API for any plugin they may like.

For details on writing plugins see the :py:class:`~.utils.plugin_base.PluginBase` class.


** UNDER CONSTRUCTION **
