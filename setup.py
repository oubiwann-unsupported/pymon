import os
import sys

import glob
from distutils.core import setup

version = open('VERSION').read().strip()

plugins = glob.glob(os.path.join('plugins', '*'))
schemas = glob.glob(os.path.join('etc', 'schema*.xml'))

setup(name="PyMonitor",
    version=version,
    description="Python Enterprise Monitoring Application",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://pymon.sf.net",
    license="BSD",
    long_description='''pymon is an open source network and process
        monitoring solution implemented in python. The interface and
        conifiguration is designed to be easily and rapidly deployed,
        saving on time and overhead often associated with other 
        monitoring solutions.''',
    packages=[
        'pymon',
        'pymon.clients',
        #'pymon.storage',
        'pymon.ui',
        #'pymon.ui.jabber',
        #'pymon.ui.irc',
        'pymon.ui.shell',
        'pymon.ui.web',
        'pymon.workflow',
    ],
    package_dir = {
        'pymon': 'pymon',
    },
    zip_safe=False,
    data_files=[
        ('etc', ['etc/pymon.conf']),
        ('etc', schemas),
        ('data', ['data/.placeholder']),
        ('plugins', plugins),
        ('service', ['service/run']),
        ('service/log', ['service/log/run']),
        ('service/log/main', ['service/log/main/.placeholder']),
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
