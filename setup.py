import os
import sys
import glob
import pwd, grp
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

if not os.path.exists('etc/pymon.conf'):
    print """
Um, you have *obviously* not read the INSTALL carefully enough.
Don't make me slap you from back in time, through your monitor. 
I swear I'll do it. Read the INSTALL again, make the appropriate
changes, and then rerun setup.py.
"""
    sys.exit()

# Dependency Checks
os.system("%s presetup.py" % sys.executable)

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
        'pymon': 'lib',
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
    scripts = ['bin/pymon', 'bin/pymon.tac'],
    classifiers = [f.strip() for f in """
    License :: OSI-Approved Open Source :: BSD License
    Development Status :: 3 - Alpha
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
os.system("%s postsetup.py" % sys.executable)

