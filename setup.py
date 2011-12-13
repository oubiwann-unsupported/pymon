import os
import sys

import glob

from setuptools import find_packages, setup
from pkg_resources import parse_requirements

from pymon import meta


try:
    parse_requirements(meta.requirements)
except:
    msg = ("You seem to be running a very old version of setuptools. "
           "This version of setuptools has a bug parsing dependencies, "
           "so automatic dependency resolution is disabled.")
    print msg


plugins = glob.glob(os.path.join('plugins', '*'))
schemas = glob.glob(os.path.join('etc', 'schema*.xml'))


setup(name="PyMonitor",
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license="BSD",
    long_description=meta.long_description,
    packages=find_packages('pymon'),
    install_requires=meta.requirements,
    include_package_data=True,
    zip_safe=False,
    package_dir = {
        'pymon': 'pymon',
    },
    zip_safe=False,
    data_files=[
        ('etc', ['etc/pymon.conf']),
        ('etc', schemas),
        ('plugins', plugins),
    ],
    scripts = ['bin/pymond', 'bin/pymon.tac'],
    classifiers = [f.strip() for f in """
    License :: OSI-Approved Open Source :: BSD License
    Development Status :: 4 - Beta
    Intended Audience :: by End-User Class :: System Administrators
    Intended Audience :: Developers
    Intended Audience :: by End-User Class :: Advanced End Users
    Intended Audience :: by Industry or Sector :: Information Technology
    Intended Audience :: by Industry or Sector :: Telecommunications Industry
    Programming Language :: Python
    Topic :: System :: Networking :: Monitoring
    Topic :: System :: Systems Administration
    Topic :: Internet :: WWW/HTTP :: Site Management
    Topic :: Security
    Operating System :: Grouping and Descriptive Categories :: All POSIX (Linux/BSD/UNIX-like OSes)
    """.splitlines() if f.strip()],

)
