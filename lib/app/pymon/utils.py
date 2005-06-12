from adytum.app.pymon.registry import globalRegistry


class LocalTools:

  def getPasswdFromFile(self, filename):
    return file(filename).readline()

def getService(db_type):
    from adytum.app.pymon.api import storage
    return eval('storage.%s.Service' % db_type)

def updateDatabase(data):
    pass

def isInRange(datum, incl_range):
    mn, mx = incl_range.split(',')
    if int(mn) <= int(datum) <= int(mx):
        return True
    return False

def getStatus(datum, cfg):
    pass

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
