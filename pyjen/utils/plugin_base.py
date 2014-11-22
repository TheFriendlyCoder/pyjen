from six import add_metaclass
from abc import ABCMeta, abstractproperty

@add_metaclass(ABCMeta)
class PluginBase(object):
    """Abstract base class common to all PyJen API plugins"""

    @abstractproperty
    def type(self):
        """The Jenkins plugin descriptive name, used when instantiating objects of that type

        :return: Jenkins plugin descriptive name, used when instantiating objects of that type
        :rtype: :func:`str`
        """
        raise NotImplementedError
