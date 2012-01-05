import os
import pwd, grp
from itertools import chain
from datetime import datetime

import pymon
from pymon.utils import getTypeFromURI, parseDate


def refreshConfig():
    conf_file = utils.getResource(['etc', 'pymon.conf'])
    conf = open(conf_file).read()
    new_md5 = md5.new(conf).hexdigest()
    old_md5 = globalRegistry.state.get('config_md5')
    globalRegistry.state['config_md5'] = new_md5
    # check against MD5 in state
    if new_md5 != old_md5:
        # get and load schema, load config
        schema_file = utils.getResource(['etc', 'schema.xml'])
        schema = ZConfig.loadSchema(schema_file)
        cfg, nil = ZConfig.loadConfig(schema, conf_file)
        # set global config to newly loaded config
        globalRegistry.config = cfg
        #if cfg.daemontools_enabled:
        #    subprocess.call('svc', '-t %s' % cfg.daemontools_service)


class Config(dict):
    """
    A YAML configuration wrapper.
    """
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

    # XXX rename to getEnabledMonitorTypes
    def getEnabledNames(self):
        '''
        Convenience function for the list of service types that are
        enabled.
        '''
        # XXX this is ugly and wrong... replacing characters like this
        # shouldn't happen at this level. This should be enforced elsewhere.
        return [x.replace(' ', '_') for x in self.monitor_status.enabled]

    def getEnabledServices(self):
        '''
        A set-powered means of geting the services.
        '''
        enabled = set(self.getEnabledNames())
        pymonServices = set(self.services.getSectionAttributes())
        return enabled.intersection(pymonServices)

    def getEnabledNotificationTypes(self):
        '''
        Get a list of the notification types that are enabled.
        '''
        return [x.replace(' ', '_') for x in self.notifications.types.enabled]

    def checkForMaintenanceWindow(self, config):
        try:
            start, end = config.scheduled_downtime.split('-')
            start = parseDate(start)
            end = parseDate(end)
        except AttributeError:
            start = end = None
        if (start <= datetime.now().timetuple() <= end):
            return True
        return False

    def checkForDisabledService(self, config):
        if config.enabled == False:
            return True
        return False

    def _getSection(self, name):
        for section in self.config.sections:
            if section.type == name:
                return SchemalessSection(section, name)

    def _getSections(self, name):
        sections = []
        for section in self.config.sections:
            if section.type == name:
                sections.append(SchemalessSection(section, name))
        return sections

    def getName(self):
        return self.config.type

    def checks(self):
        name = "%s-check" % self.config.type
        return self._getSections(name)
    checks = property(checks)

    def default(self):
        name = "%s-defaults" % self.config.type
        return self._getSections(name)[0]
    default = property(default)

    def getEnabledNames(self):
        '''
        Convenience function for the list of service types that are
        enabled.
        '''
        # XXX this is ugly and wrong... replacing characters like this
        # shouldn't happen at this level. This should be enforced elsewhere.
        enabled = self.monitor_status.enable
        if isinstance(enabled, str):
            enabled = [enabled]
        return [ x.replace(' ', '_') for x in enabled ]

    def getEnabledServices(self):
        '''
        A set-powered means of geting the services.
        '''
        enabled = set(self.getEnabledNames())
        # let's see if there are any configured for each enabled type
        for name in enabled:
            yield getattr(self.services, name)

    def getEnabledNotificationTypes(self):
        '''
        Get a list of the notification types that are enabled.
        '''
        enabled = self.notifications.types.enable
        if isinstance(enabled, str):
            enabled = [enabled]
        return [x.replace(' ', '_') for x in enabled]


    def getCheckConfigFromURI(self, uri):
        type = getTypeFromURI(uri)
        svc = self.getServiceConfigFromURI(uri)
        uri = uri.split('://')[1]
        for check in svc.checks:
            if check.uri == uri:
                return check

    def getDefaultsFromURI(self, uri):
        type = getTypeFromURI(uri)
        svc = self.getServiceConfigFromURI(uri)
        return getattr(svc, '%s_defaults' % type)

    def getServiceConfigFromURI(self, uri):
        type = getTypeFromURI(uri)
        uri = uri.split('://')[1]
        return getattr(self.services, type)

    def configFactory(self, uri):
        return CheckConfig(uri)


class CheckConfig(object):
    """
    The purpse of this class is clarity and convenience. In particular, it
    provides three attributes, each for the three different types of configs
    needed by any given pymon monitor:
        1. the general, application-wide configuration
        2. the defaults for the given monitor type, and
        3. the monitor-specific confniguration (e.g., hostname to check)
    """
    def __init__(self, uri):
        self.uri = uri

    def app(self):
        return cfg
    app = property(app)

    def defaults(self):
        return cfg.getDefaultsFromURI(self.uri)
    defaults = property(defaults)

    def check(self):
        return cfg.getCheckConfigFromURI(self.uri)
    check = property(check)


class ConfigMain(Config):
    """
    """
    def __init__(self, *args, **kwargs):
        super(ConfigMain, self).__init__(*args, **kwargs)
        self.stateLookup = dict(
            [(y,x) for x, y in self['state definitions'].items()])

    def getPymonUserGroup(self):
        user = pwd.getpwnam(self['system user'])
        group = grp.getgrnam(self['system group'])
        return (user, group)

    def getStateNames(self):
        return sorted(self['state definitions'].keys())

    def getStateNumbers(self):
        return sorted(self['state definitions'].values())

    def getStateNameFromNumber(self, num):
        return self.stateLookup[int(num)]

    def getStateNumberFromName(self, name):
        return self['state definitions'][name]


class ConfigMonitors(Config):
    """
    """


class ConfigAPI(object):

    def __init__(self, mainConfigDict, monitorsConfigDict):
        self.main = ConfigMain(mainConfigDict)
        self.monitors = ConfigMonitors(monitorsConfigDict)

    @property
    def isMaintenance(self):
        if (
            self.main.checkForMaintenanceWindow() == True or
            self.monitors.checkForMaintenanceWindow() == True):
            return True
        return False

    @property
    def isDisabled(self):
        if (
            self.main.checkForDisabledService() == True or
            self.monitors.checkForDisabledService() == True):
            return True
        return False

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
