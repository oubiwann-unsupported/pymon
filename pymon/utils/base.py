from uri import Uri


class LocalTools:

    def getPasswdFromFile(self, filename):
        return file(filename).readline()


def getService(db_type):
    from pymon.api import storage
    return eval('storage.%s.Service' % db_type)


def updateDatabase(data):
    pass


def isInList(datum, values):
    if isinstance(values, str):
        values = [x.strip() for x in values.split(',')]
    values = [unicode(x) for x in values]
    if unicode(datum) in values:
        return True
    return False


def _isInRange(datum, dataRange, delimiter, function):
    dataRange = [function(x) for x in dataRange.split(delimiter)]
    dataRange[1] += 1
    if function(datum) in xrange(*dataRange):
        return True
    else:
        return False


def isInNumericRange(datum, threshold, delimiter='-'):
    return _isInRange(datum, threshold, delimiter, int)


def isInCharacterRange(datum, threshold, delimiter='-'):
    return _isInRange(datum, threshold, delimiter, ord)


def isInRange(datum, threshold, delimiter='-'):
    try:
        int(datum)
        return isInNumericRange(datum, threshold, delimiter)
    except ValueError:
        return isInCharacterRange(datum, threshold, delimiter)


def isExactly(datum, threshold):
    if unicode(datum) == unicode(threshold):
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
    parsed = Uri(uri)
    # get scheme
    scheme = parsed.getScheme()
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


def getSimplePlural(word, count):
    if count > 1:
        word += 's'
    return word
