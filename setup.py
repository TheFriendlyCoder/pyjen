from setuptools import setup
import pyjen
import pkgutil
import os

pyjen_packages = []
for loader, module_name, is_pkg in pkgutil.walk_packages(os.path.join(os.path.curdir, "pyjen")):
    if is_pkg and module_name.startswith("pyjen"):
        pyjen_packages.append(module_name)

setup(
    name='pyjen',
    version=pyjen.VERSION,
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    packages=pyjen_packages,
    description='Python wrapper for the Jenkins CI REST API',
    long_description=open('README.rst').read(),
    url='https://github.com/TheFriendlyCoder/pyjen',
    install_requires=["requests>=2.0.1"],
    classifiers=[
                   "Development Status :: 3 - Alpha",
                   "Environment :: Console",
                   "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.3",
                   "Topic :: Software Development :: Libraries"]
)
