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

        :return: Jenkins plugin descriptive name, used when instantiating objects of that type
        :rtype: :class:`str`
        """
        raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    pass
