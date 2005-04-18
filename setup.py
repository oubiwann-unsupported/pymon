#!/usr/bin/env python

import os
import sys
import glob
import pwd, grp
from distutils.core import setup
from lib.app.pymon.constants import INSTALL_DIR, USER, GROUP, \
    CONFIG_DIR, CONFIG_INI, CONFIG_XML, PLUGINS_DIR


try:
    uid = pwd.getpwnam(USER)[2]
    gid = grp.getgrnam(GROUP)[2]
except KeyError:
    print "\nNon-system user or group name given. Did you edit your config file?\n"
    sys.exit()

plugins = glob.glob('%s/*.py' % PLUGINS_DIR)

setup(name="PyMonitor",
    version="1.1",
    description="Python Monitoring Application",
    author="Duncan McGreggor",
    author_email="duncan@adytumsolutions.com",
    url="http://adytum.us",
    packages=[
        'adytum',
        'adytum.app',
        'adytum.app.pymon',
        'adytum.app.pymon.adaptors',
        'adytum.app.pymon.storage',
        'adytum.app.pymon.ui',
        'adytum.app.pymon.ui.jabber',
        'adytum.app.pymon.ui.irc',
        'adytum.app.pymon.ui.shell',
        'adytum.app.pymon.ui.web',
        'adytum.config',
        'adytum.net',
        'adytum.net.http',
        'adytum.os',
    ],
    package_dir = {'adytum': 'lib'},
    data_files=[
        ('%s/bin' % INSTALL_DIR, ['bin/pymon.tac']),
        ('%s/%s' % (INSTALL_DIR, CONFIG_DIR), ['conf/%s' % CONFIG_INI]),
        ('%s/%s' % (INSTALL_DIR, CONFIG_DIR), ['conf/%s' % CONFIG_XML]),
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
