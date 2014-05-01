from setuptools import setup

setup(
    name='pyjen',
    version='0.0.2dev',
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    license=open('LICENSE.txt').read(),
    packages=['pyjen', 'pyjen.utils', 'pyjen.plugins'],
    description='Python wrapper for the Jenkins CI REST API',
    long_description=open('README.rst').read(),
    url='https://github.com/TheFriendlyCoder/pyjen',
    install_requires = ["requests>=2.0.1"]
)
