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

def getStateNameFromNumber(num):
    states = globalRegistry.config.state_definitions

    for state in states.getSectionAttributes():
        check = getattr(states, state)
        if check == num:
            return state

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
    uri = uri.split('://')[1]
    checks = getattr(cfg.services, type).checks
    for check in checks:
        if check.uri == uri:
            return check

def getDefaultsFromUri(uri):
    cfg = globalRegistry.config
    type = getTypeFromUri(uri)
    uri = uri.split('://')[1]
    return getattr(cfg.services, type).defaults

def getMailList(uri):
    defs = getDefaultsFromUri(uri)
    service_cfg = getEntityFromUri(uri)
    # check defaults for notification-list-replace
    base = globalRegistry.config.notification_list
    def_replace = defs.notification_list_replace
    def_append = defs.notification_list_append
    svc_replace = service_cfg.notification_list_replace
    svc_append = service_cfg.notification_list_append
    mail_list = base.emails
    if svc_replace:
        return svc_replace.emails
    if def_replace:
        return def_replace.emails
    if svc_append:
        mail_list.extend(svc_append.emails)
    if def_append:
        mail_list.extend(def_append.emails)
    return mail_list
        

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()

