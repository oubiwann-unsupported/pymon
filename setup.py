#!/usr/bin/env python

from distutils.core import setup

INSTALL_DIR='/usr/local/pymon'

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
        'adytum.net',
        'adytum.net.http',
        'adytum.os',
    ],
    package_dir = {'adytum': 'lib'},
    data_files=[
        ('%s/bin' % INSTALL_DIR, ['bin/pymon.tac']),
        ('%s/conf' % INSTALL_DIR, ['conf/pymon.ini']),
        ('%s/data' % INSTALL_DIR, ['data/.placeholder']),
        ('%s/service' % INSTALL_DIR, ['service/run']),
        ('%s/service/log' % INSTALL_DIR, ['service/log/run']),
        ('%s/service/log/main' % INSTALL_DIR, ['service/log/main/.placeholder']),
    ],
)
