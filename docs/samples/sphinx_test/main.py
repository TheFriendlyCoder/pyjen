# Implementation file used during development to verify Sphinx syntax for certain primitives

# Helpful Links:
# http://sphinx-doc.org/domains.html#signatures
# https://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
# http://docutils.sourceforge.net/docs/user/rst/quickref.html
"""
* strings: :class:`str`
* floats: :class:`float`
* ints: :class:`int`
* lists: :class:`list`
* booleans: :class:`bool`
* tuples: :func:`tuple`
"""

class MyClass (object):
    """Some descriptive text for my class

    here is some more detailed info here
    """
    def __init__(self, p1):
        """Constructor

        :param p1: First parameter is a list
        :type p1: :class:`list`
        """
        pass

    def method1 (self, p1):
        """My method description

        :param float p1: some floating point value
        """
        pass

class MyClassDerived(MyClass):
    def __init__(self, p1):
        """Constructor derived

        :param str p1: some derived value
        """
        pass

    def SomeOtherMethod(self):
        """Yet another method"""
        pass


class MyClass2():
    """Class description would go here"""

    def __init__(self):
        """Constructor"""
        pass

    def MyMethod(self, obj):
        """Some method

        Makes use of local method :meth:`.SomeOtherMethod`

        Could have also used full class notation :meth:`MyClass2.SomeOtherMethod`

        :param obj: first parameter should be of type 'MyClassDerived'
        :type obj: :class:`MyClassDerived`

        """
        pass

    def SomeOtherMethod(self):
        """Description of some other method"""
        pass

def someFn(p1):
    """My description

    For an example of a short-form link see :py:meth:`~MyClass2.MyMethod`

    :param str p1: Here is parameter one
    """
    pass

if __name__ == "__main__":
    print("hello")
