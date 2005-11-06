from pymon.registry import globalRegistry


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

def isInList(datum, list_string):
    '''
    >>> test_list = '200, 303, 304, 401'
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

def getStateNameFromNumber(num):
    cfg = globalRegistry.config
    states = dict([ (val, key) for key, val in cfg.constants.states.items() ])
    return states.get(num)

def makeUri(scheme, uri_remainder):
    return (('%s://%s') % (scheme, uri_remainder)).replace(' ', '+')

def getTypeFromUri(uri):
    from adytum.util.uri import Uri
    # parse URI
    uri = Uri(uri)
    # get scheme
    scheme = uri.getScheme()
    return scheme.replace('+', ' ')

def getEntityFromUri(uri):
    cfg = globalRegistry.config
    type = getTypeFromUri(uri)
    remainder = uri.split('://')[1]
    return cfg.services.service(type=type).entries.entry(uri=remainder)

def getDefaultsFromUri(uri):
    cfg = globalRegistry.config
    type = getTypeFromUri(uri)
    remainder = uri.split('://')[1]
    return cfg.services.service(type=type).defaults

def getMailList(uri):
    defs = getDefaultsFromUri(uri)
    service_cfg = getEntityFromUri(uri)
    # XXX currently, this only supports the first escalation level
    if service_cfg.escalation:
        esc = service_cfg.escalation.group(level='0')
    else:
        esc = defs.escalation.group(level='0')
    return esc.maillist.email

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()

