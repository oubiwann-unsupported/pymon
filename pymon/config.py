import os
from datetime import datetime

from pkg_resources import resource_filename
from pkg_resources import Requirement
from pkg_resources import DistributionNotFound

import ZConfig

from adytum.util.uri import Uri

egg_pkg_name = "PyMonitor"
schema_file = "etc/schema.xml"
config_file = "etc/pymon.conf"
try:
    schema_file = resource_filename(Requirement.parse(egg_pkg_name),
        schema_file)
    config_file = resource_filename(Requirement.parse(egg_pkg_name),
        config_file)
except DistributionNotFound:
    pass

schema = ZConfig.loadSchema(schema_file)
cfg, nil = ZConfig.loadConfig(schema, config_file)

# now that we've got the config file, we can get the prefix and then
# check to see if there is an override on the filesystem for SonicVault
# configuration. If so, we will override the one in the python lib.
prefix = cfg.prefix.split('/')
config_file = os.path.sep + os.path.join(*prefix+['etc', 
    'pymon.conf'])
if os.path.exists(config_file):
    cfg, nil = ZConfig.loadConfig(schema, config_file)

def getResource(rsrc_list):
    prefix = cfg.prefix.split('/')
    rel_path = '/'.join(rsrc_list)
    local_path = './'+rel_path
    abs_path = os.path.sep + os.path.join(*prefix+rsrc_list)
    # check install dir first
    if os.path.exists(abs_path):
        return abs_path
    # then check current dir
    elif os.path.exists(local_path):
        return local_path
    # when those don't return anything, look in the egg
    else:
        return resource_filename(Requirement.parse(egg_pkg_name),
            rel_path)

stateLookup = dict([ 
    (getattr(cfg.state_definitions, x), x) 
    for x in cfg.state_definitions.getSectionAttributes()])

def getStateNames():
    return stateLookup.values()

def getStateNumbers():
    return stateLookup.keys()

def getStateNameFromNumber(num):
    return stateLookup[num]

def getStateNumberFromName(name):
    return getattr(cfg.state_definitions, name.lower())

def makeUID(scheme, uri_remainder):
    return (('%s://%s') % (scheme, uri_remainder)).replace(' ', '+')

def getTypeFromURI(uri):
    from adytum.util.uri import Uri
    # parse URI
    uri = Uri(uri)
    # get scheme
    scheme = uri.getScheme()
    return scheme.replace('+', ' ')

def getFriendlyTypeFromURI(uri):
    return getTypeFromURI(uri).replace('_', ' ')

def getCheckConfigFromURI(uri):
    type = getTypeFromURI(uri)
    uri = uri.split('://')[1]
    checks = getattr(cfg.services, type).checks
    for check in checks:
        if check.uri == uri:
            return check

def getDefaultsFromURI(uri):
    type = getTypeFromURI(uri)
    uri = uri.split('://')[1]
    return getattr(cfg.services, type).defaults

def getServiceConfigFromURI(uri):
    type = getTypeFromURI(uri)
    uri = uri.split('://')[1]
    return getattr(cfg.services, type)

def getHostFromURI(uri):
    return Uri(uri).getAuthority().getHost()

def getServicesOfType(serviceName):
    return getattr(cfg.services, serviceName)

def getMailList(uri):
    defs = getDefaultsFromURI(uri)
    service_cfg = getCheckConfigFromURI(uri)
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

def getEnabledNames():
    '''
    Convenience function for the list of service types that are 
    enabled.
    '''
    # XXX this is ugly and wrong... replacing characters like this
    # shouldn't happen at this level. This should be enforced elsewhere.
    return [ x.replace(' ', '_') for x in cfg.monitor_status.enabled ]

def getEnabledServices():
    '''
    A set-powered means of geting the services.
    '''
    enabled = set(getEnabledNames())
    pymonServices = set(cfg.services.getSectionAttributes())
    return enabled.intersection(pymonServices)

def checkForMaintenanceWindow(config):
    # Checking for maintenance window...
    try:
        start = config.scheduled_downtime['start'].timetuple()
        end = config.scheduled_downtime['end'].timetuple()
        now = datetime.now().timetuple()
    except TypeError:
        start = end = now = None
    except AttributeError:
        if self.checkConfig == None:
            raise "Configuration should not be none!"
    if (start < now < end):
        # Maintenance is scheduled for this service now
        return True
    # No maintenance window for this time
    return False
