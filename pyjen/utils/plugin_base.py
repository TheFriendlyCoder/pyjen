"""Declaration for abstract base class to be used by all PyJen plugins"""
from six import add_metaclass
from abc import ABCMeta, abstractproperty


@add_metaclass(ABCMeta)
class PluginBase(object):
    """Abstract base class common to all PyJen API plugins

    All PyJen plugins must derive from this class and implement its abstract interface
    """

    @abstractproperty
    def type(self):
        """The Jenkins plugin descriptive name, used when instantiating objects of that type

        Some examples from the built-in plugins are:

        * "hudson.scm.NullSCM"
        * "hudson.scm.SubversionSCM"
        * "hudson.model.MyView"

        These names can typically be copied verbatim from the XML node in the Jenkins config.xml
        for the entity that describes the plugin properties. The name should be defined by an
        XML attribute named "class". Here is an example of the SVN plugin XML ::

            <scm class="hudson.scm.SubversionSCM" plugin="subversion@2.3">

        For plugins that extend Jenkins native objects like views and jobs the plugin name
        will be defined in the name of the tag itself, like this ::

            <hudson.plugins.nested__view.NestedView plugin="nested-view@1.14">

        TIP: When implementing this property on a concrete class, you will need to declare a static class
        attribute for the PyJen plugin API to work correctly, something like ::

            class MyClass(PluginBase):
                type = "my.name.of.plugin"

        :return: Jenkins plugin descriptive name, used when instantiating objects of that type
        :rtype: :class:`str`
        """
        raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    pass
