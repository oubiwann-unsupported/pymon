import os
import pwd, grp                         
from datetime import datetime

from pkg_resources import resource_filename
from pkg_resources import Requirement
from pkg_resources import DistributionNotFound

import ZConfig

from pymon.utils import getTypeFromURI

egg_pkg_name = "PyMon"
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
config, nil = ZConfig.loadConfig(schema, config_file)

# now that we've got the config file, we can get the prefix and then
# check to see if there is an override on the filesystem for the
# configuration. If so, we will override the one in the installed python
# package.
prefix = config.prefix.split('/')
config_file = os.path.sep + os.path.join(*prefix+['etc',
    'pymon.conf'])
if os.path.exists(config_file):
    config, nil = ZConfig.loadConfig(schema, config_file)

# ideally, this would be in utils. Need to figure out the nicest way to avoid
# import loops and restructure the code accordingly in order to move this.
def getResource(rsrc_list):
    prefix = config.prefix.split('/')
    rel_path = '/'.join(rsrc_list)
    local_path = './'+rel_path
    abs_path = os.path.sep + os.path.join(*prefix+rsrc_list)
    # check install dir first
    if os.path.exists(abs_path):
        return abs_path
    # then check current dir
    elif os.path.exists(local_path):
        return os.path.abspath(local_path)
    # when those don't return anything, look in the egg
    else:
        return resource_filename(Requirement.parse(egg_pkg_name),
            rel_path)


class Config(object):
    """
    A ZConfig wrapper.
    """
    def __init__(self, config):
        self.config = config
        self.__dict__.update(config.__dict__)
        self.stateLookup = dict([
            (getattr(config.state_definitions, x), x)
            for x in config.state_definitions.getSectionAttributes()])

    def __getattr__(self, attr):
        try:
            return self.__dict__.get(attr)
        except AttributeError:
            return self.config.__getattr__(attr)
                                        
    def getPymonUserGroup(self):
        user = pwd.getpwnam(self.user)[2]        
        group = grp.getgrnam(self.group)[2]   
        return (user, group)

    def getCheckConfigFromURI(self, uri):
        type = getTypeFromURI(uri)
        uri = uri.split('://')[1]
        checks = getattr(self.services, type).checks
        for check in checks:
            if check.uri == uri:
                return check

    def getDefaultsFromURI(self, uri):
        type = getTypeFromURI(uri)
        uri = uri.split('://')[1]
        return getattr(self.services, type).defaults

    def getServiceConfigFromURI(self, uri):
        type = getTypeFromURI(uri)
        uri = uri.split('://')[1]
        return getattr(self.services, type)

    def getServicesOfType(self, serviceName):
        return getattr(self.services, serviceName)

    def getMailList(self, uri):
        defs = self.getDefaultsFromURI(uri)
        service_cfg = self.getCheckConfigFromURI(uri)
        # check defaults for notification-list-replace
        base = self.notifications.list
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

    def getEnabledNames(self):
        '''
        Convenience function for the list of service types that are 
        enabled.
        '''
        # XXX this is ugly and wrong... replacing characters like this
        # shouldn't happen at this level. This should be enforced elsewhere.
        return [ x.replace(' ', '_') for x in self.monitor_status.enabled ]

    def getEnabledServices(self):
        '''
        A set-powered means of geting the services.
        '''
        enabled = set(self.getEnabledNames())
        pymonServices = set(self.services.getSectionAttributes())
        return enabled.intersection(pymonServices)

    def checkForMaintenanceWindow(self, config):
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

    def getStateNames(self):
        return self.stateLookup.values()

    def getStateNumbers(self):
        return self.stateLookup.keys()

    def getStateNameFromNumber(self, num):
        return self.stateLookup[num]

    def getStateNumberFromName(self, name):
        return getattr(self.state_definitions, name.lower())

cfg = Config(config)

