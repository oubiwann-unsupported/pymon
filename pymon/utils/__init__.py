from datetime import datetime

from uri import Uri

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

def parseDate(yyyymmdd_hhmmss_string):
    date, time = yyyymmdd_hhmmss_string.strip().split()
    y, m, d = date.strip().split('.')
    h, min, s = time.strip().split(':')
    return tuple([ int(x) for x in (y,m,d,h,min,s) ])

def makeUID(scheme, uri_remainder):
    return (('%s://%s') % (scheme, uri_remainder)).replace(' ', '+')

def getTypeFromURI(uri):
    # parse URI
    uri = Uri(uri)
    # get scheme
    scheme = uri.getScheme()
    return scheme.replace('+', ' ')

def getFriendlyTypeFromURI(uri):
    return getTypeFromURI(uri).replace('_', ' ')

def getHostFromURI(uri):
    return Uri(uri).getAuthority().getHost()

def guessMonitorFactoryNameFromType(checkType):
    """
    This is intended to be used in pymon.monitors.AbstractFactory, particularly
    in makeMonitor() when a factory has not been set/defined in a configuration
    file.
    """
    part = checkType.replace('_', ' ').title().replace(' ', '')
    return "%sMonitor" % part

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()
