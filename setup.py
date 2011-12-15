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


setup(name="PyMonitor",
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license="BSD",
    long_description=meta.long_description,
    packages=find_packages('.'),
    install_requires=meta.requirements,
    include_package_data=True,
    zip_safe=False,
    data_files=[
        ('etc', ['etc/pymon.conf', 'etc/schema.xml']),
        ('etc/services/http_status', [
                 'etc/services/http_status/www.adytum.us.conf',
                 'etc/services/http_status/www2.adytum.us.conf']),
        ('etc/services/ping', [
                 'etc/services/ping/shell1.adytum.us.conf',
                 'etc/services/ping/shell2.adytum.us.conf',
                 'etc/services/ping/svn.adytum.us.conf'])
    ],
    scripts = ['bin/pymond'],
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
