import sys
import md5
import subprocess

import ZConfig

from logger import log
from config import cfg
from config import getResource
from registry import globalRegistry

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
    states = cfg.state_definitions

    for state in states.getSectionAttributes():
        check = getattr(states, state)
        if check == num:
            return state.strip()

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
    type = getTypeFromUri(uri)
    uri = uri.split('://')[1]
    checks = getattr(cfg.services, type).checks
    for check in checks:
        if check.uri == uri:
            return check

def getDefaultsFromUri(uri):
    type = getTypeFromUri(uri)
    uri = uri.split('://')[1]
    return getattr(cfg.services, type).defaults

def getMailList(uri):
    defs = getDefaultsFromUri(uri)
    service_cfg = getEntityFromUri(uri)
    # check defaults for notification-list-replace
    base = cfg.notifications.list
    def_replace = defs.notification_list_replace
    def_append = defs.notification_list_append
    svc_replace = service_cfg.notification_list_replace
    svc_append = service_cfg.notification_list_append
    mail_list = []
    mail_list.extend(base.emails)
    if svc_replace:
        return svc_replace.emails
    if def_replace:
        return def_replace.emails
    if svc_append:
        mail_list.extend(svc_append.emails)
    if def_append:
        mail_list.extend(def_append.emails)
    return mail_list

def refreshConfig():
    log.info("Checking for config file changes...")
    conf_file = getResource(['etc', 'pymon.conf'])
    conf = open(conf_file).read()
    new_md5 = md5.new(conf).hexdigest()
    old_md5 = globalRegistry.state.get('config_md5')
    globalRegistry.state['config_md5'] = new_md5
    # check against MD5 in state
    if new_md5 != old_md5:
        log.warning("Config MD5 signatures do not match; loading new config...")
        # get and load schema, load config
        schema_file = getResource(['etc', 'schema.xml'])
        schema = ZConfig.loadSchema(schema_file)
        cfg, nil = ZConfig.loadConfig(schema, conf_file)
        # set global config to newly loaded config
        globalRegistry.config = cfg
        #if cfg.daemontools_enabled:
        #    subprocess.call('svc', '-t %s' % cfg.daemontools_service)

def _test():
    import doctest, utils
    return doctest.testmod(utils)

if __name__ == '__main__':
    _test()

