from setuptools import setup

setup(
    name='pyjen',
    version='0.0.1dev',
    author='Kevin S. Phillips',
    author_email='kevin@thefriendlycoder.com',
    license='LICENSE.txt',
    packages=['pyjen'],
    description='Python wrapper for the Jenkins CI REST API',
    long_description=open('README.md').read(),
    url='https://github.com/TheFriendlyCoder/pyjen',
    requires = ["requests(>=2.0.1)"]
)
