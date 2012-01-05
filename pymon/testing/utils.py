import os

import yaml

from pymon.testing import data


def getDataDir():
    return data.__path__[0]


def _loadYAML(filename):
    fh = open(filename)
    data = yaml.load(fh)
    fh.close()
    return data
    

def loadGeneralYAML():
    filename = os.path.join(getDataDir(), "pymon_config.yaml")
    return _loadYAML(filename)


def loadMonitorYAML():
    filename = os.path.join(getDataDir(), "pymon_service_checks.yaml")
    return _loadYAML(filename)
