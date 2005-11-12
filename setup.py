import ez_setup
ez_setup.use_setuptools()

# XXX do search/replace templating in in the example-pymonl.xml
# file, and write it out to the final file. 
# XXX delete constants.py file, after removing all references to it.
INSTALL_DIR     = '/usr/local/pymon'
USER            = 'pymon'
GROUP           = 'pymon'
TYPE            = 'service type'
CONFIG_DIR      = 'conf'
CONFIG_INI      = 'pymon.ini'
CONFIG_XML      = 'pymon.xml'
PLUGINS_DIR     = 'plugins'
PYMON_APP       = 'bin/pymon.tac'
TWISTD          = '/usr/local/bin/twistd'

import os
import sys
import glob
import pwd, grp
try:
    # if you want to build python egg dist files,
    # you'll need the latest version of setuptools
    # You can get it in the nondist/sandbox/setuptools
    # directory in a python cvs checkout.
    from setuptools import setup
except:
    from distutils.core import setup
from lib.pymon.constants import INSTALL_DIR, USER, GROUP, \
    CONFIG_DIR, CONFIG_INI, CONFIG_XML, PLUGINS_DIR

# Dependancy Checks
try:
    uid = pwd.getpwnam(USER)[2]
    gid = grp.getgrnam(GROUP)[2]
except KeyError:
    print """\nNon-system user or group name given. 
Did you edit the ./lib/app/pymon/constants.py file?\n"""
    sys.exit()
try:
    #import ElementTree
    import cElementTree
except:
    print "\nYou will need ElementTree and cElementTree to run pymon.\n"
    sys.exit()
try:
    from sqlobject import SQLObject
except:
    print "\nYou will need to have sqlobject installed to run pymon.\n"
    sys.exit()

plugins = glob.glob('%s/*.py' % PLUGINS_DIR)

setup(name="PyMonitor",
    version="0.3.2",
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
        'pymon.storage',
        'pymon.ui',
        'pymon.ui.jabber',
        'pymon.ui.irc',
        'pymon.ui.shell',
        'pymon.ui.web',
        'pymon.workflow',
        'adytum',
        'adytum.net',
        'adytum.os',
        'adytum.util',
        'adytum.workflow',
    ],
    package_dir = {
        'pymon': 'lib/pymon',
        'adytum': 'lib',
    },
    data_files=[
        ('bin', ['bin/pymon.tac', 'bin/pymon']),
        ('%s' % (CONFIG_DIR), ['conf/example-pymon.conf']),
        ('%s' % (CONFIG_DIR), ['conf/schema.xml']),
        ('data', ['data/.placeholder']),
        ('%s' % (PLUGINS_DIR), plugins),
        ('service', ['service/run']),
        ('service/log', ['service/log/run']),
        ('service/log/main', ['service/log/main/.placeholder']),
    ],
    scripts = ['bin/pymon'],
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

# Set the permissions on the install directory
'''
print "Changing ownership of %s to %s:%s (%s:%s)..." % (INSTALL_DIR, USER, GROUP, uid, gid)
for fullpath, dirs, files in os.walk(INSTALL_DIR):
    #print fullpath, dirs, files
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)
'''
