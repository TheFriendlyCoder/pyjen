from setuptools import setup

setup(
    name='pyjen',
    version='0.0.9dev',
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    packages=['pyjen', 'pyjen.utils', 'pyjen.plugins'],
    description='Python wrapper for the Jenkins CI REST API',
    long_description=open('README.rst').read(),
    url='https://github.com/TheFriendlyCoder/pyjen',
    install_requires = ["requests>=2.0.1"],
    classifiers = [
                   "Development Status :: 3 - Alpha",
                   "Environment :: Console",
                   "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.3",
                   "Topic :: Software Development :: Libraries"]
)
