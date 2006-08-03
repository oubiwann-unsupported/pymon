import os
import sys
from subprocess import call

if not os.path.exists('etc/pymon.conf'):
    print """
Um, you have *obviously* not read the INSTALL carefully enough.
Don't make me slap you from back in time, through your monitor. 
I swear I'll do it. Read the INSTALL again, make the appropriate
changes, and then rerun setup.py.

Yes, you still have to do this if you are updating/reinstalling.
We don't know where you installed it, so you have to tell us
by providing an 'etc/pymon.conf' with a prefix. Sooner or later,
we'll get around to using a --prefix option in the install...
"""
    sys.exit()

# Dependency Checks
ret = call([sys.executable, 'presetup.py'])
if ret != 0:
    print "\nThere was a problem running the pre-setup script.\n"
    sys.exit()

import twisted
if twisted.__version__ < '2.1.0':
    print "Sorry, you need to have Twisted 2.1.0 or greater installed."
    sys.exit()

import glob
import pwd, grp
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

plugins = glob.glob(os.path.join('plugins', '*.py'))
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
    install_requires=[
        'Adytum-PyMonitor >= 1.0.4',
    ],
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

# finish up
ret = call([sys.executable, 'postsetup.py'])
if ret != 0:
    print "\nThere was a problem running the post-setup script.\n"
    sys.exit()



