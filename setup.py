#!/usr/bin/env python

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
from lib.app.pymon.constants import INSTALL_DIR, USER, GROUP, \
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
    author_email="duncan@adytumsolutions.com",
    url="http://pymon.sf.net",
    license="BSD",
    long_description='''pymon is an open source network and process
        monitoring solution implemented in python. The interface and
        conifiguration is designed to be easily and rapidly deployed,
        saving on time and overhead often associated with other 
        monitoring solutions.''',
    packages=[
        'adytum',
        'adytum.app',
        'adytum.app.pymon',
        'adytum.app.pymon.clients',
        'adytum.app.pymon.storage',
        'adytum.app.pymon.ui',
        'adytum.app.pymon.ui.jabber',
        'adytum.app.pymon.ui.irc',
        'adytum.app.pymon.ui.shell',
        'adytum.app.pymon.ui.web',
        'adytum.app.pymon.workflow',
        'adytum.config',
        'adytum.net',
        'adytum.net.http',
        'adytum.os',
        'adytum.util',
        'adytum.workflow',
    ],
    package_dir = {'adytum': 'lib'},
    data_files=[
        ('%s/bin' % INSTALL_DIR, ['bin/pymon.tac']),
        ('%s/%s' % (INSTALL_DIR, CONFIG_DIR), ['conf/example-pymon.ini']),
        ('%s/%s' % (INSTALL_DIR, CONFIG_DIR), ['conf/example-pymon.xml']),
        ('%s/data' % INSTALL_DIR, ['data/.placeholder']),
        ('%s/%s' % (INSTALL_DIR, PLUGINS_DIR), plugins),
        ('%s/service' % INSTALL_DIR, ['service/run']),
        ('%s/service/log' % INSTALL_DIR, ['service/log/run']),
        ('%s/service/log/main' % INSTALL_DIR, ['service/log/main/.placeholder']),
    ],
)

# Set the permissions on the install directory
print "Changing ownership of %s to %s:%s (%s:%s)..." % (INSTALL_DIR, USER, GROUP, uid, gid)
for fullpath, dirs, files in os.walk(INSTALL_DIR):
    #print fullpath, dirs, files
    os.chown(fullpath, uid, gid)
    for filename in files:
        os.chown(os.path.join(fullpath, filename), uid, gid)
