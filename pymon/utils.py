import sys
import md5
import subprocess
import logging as log

import ZConfig

import simplejson

from config import cfg
from config import getResource

log_level = eval('log.%s' % cfg.log_level)
log.basicConfig(level=log_level,
    format='%(levelname)-8s %(message)s',
    stream=sys.stdout,
)
class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()

def getService(db_type):
    from pymon.api import storage
    return eval('storage.%s.Service' % db_type)

def updateDatabase(data):
    pass

def isInRange(datum, incl_range):
    minimum, maximum = incl_range.split(',')
    if int(minimum) <= int(datum) <= int(maximum):
        return True
    return False

def isInList(datum, in_list):
    '''
    >>> test_list = [200, 303, 304, 401]
    >>> isInList(200, test_list)
    True
    >>> isInList('200', test_list)
    True
    >>> isInList('405', test_list)
    False
    '''
    list = [ x.strip() for x in list_string.split(',') ]
    if str(datum) in list:
        return True
    return False

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()

