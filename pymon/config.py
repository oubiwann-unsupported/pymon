import os
import pwd, grp
from itertools import chain
from StringIO import StringIO
from datetime import datetime

from ZConfig.schemaless import loadConfigFile

import pymon
from pymon.utils import getTypeFromURI, parseDate


# XXX this should probably be moved into utils
def getPyMonDir():
    return os.path.dirname(pymon.__file__)


def getBaseDir():
    return os.path.dirname(getPyMonDir())


def getEtcDir():
    return os.path.join(getBaseDir(), 'etc')


def getConfigFiles():
    etcServices = os.path.join(getEtcDir(), 'services')
    plugins = os.path.join(getPyMonDir(), 'plugins')
    confs = chain(os.walk(etcServices), os.walk(plugins))
    for base, dirs, files in confs:
        if not files:
            continue
        for name in files:
            if name.endswith('.conf'):
                yield "%s/%s" % (base, name)


legalEndings = ['-check', '-defaults']


def getBaseName(name):
    for end in legalEndings:
        if name.endswith(end):
            return name.split(end)[0]


# we need to iterate through the files and keep track of their opening tags so
# that we can group services together under their own tags
def assembleConfig():
    # first, let's gather all the data, grouped by tag
    groups = {}
    for path in getConfigFiles():
        fh = open(path)
        raw = fh.read()
        fh.close()
        tag = raw.lstrip().split('\n')[0].strip()
        tag = tag.replace('<', '').replace('>', '')
        if tag:
            groups.setdefault(tag, [])
            groups[tag].append(raw)
    # next, reduce all the tags to their base names
    containers = set([getBaseName(x) for x in groups.keys()])
    # now we need to group service configs according to type
    sections = ''
    for container in containers:
        sections += '<%s>\n' % container
        for tag, data in groups.items():
            if tag in [container+x for x in legalEndings]:
                for entry in data:
                    sections += entry
        sections += '</%s>\n' % container
    # now let's assemble the thing
    fh = open(os.path.join(getEtcDir(), "pymon.conf"))
    conf = fh.read() + '<services>\n%s</services>\n' % sections
    fh.close()
    configFile = StringIO(conf)
    return configFile


config = loadConfigFile(assembleConfig())


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


class BaseConfig(object):
    """
    A base configuration wrapper.
    """

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

    def getStateNames(self):
        return self.stateLookup.values()

    def getStateNumbers(self):
        return self.stateLookup.keys()

    def getStateNameFromNumber(self, num):
        return self.stateLookup[str(num)]

    def getStateNumberFromName(self, name):
        return getattr(self.state_definitions, name.lower())


class Config(BaseConfig):
    """
    A ZConfig wrapper.
    """
    def __init__(self, config):
        self.config = config
        self.__dict__.update(config.__dict__)
        self.stateLookup = dict([
            (getattr(config.state_definitions, x), x)
            for x in config.state_definitions.getSectionAttributes()])


class SchemalessSection(object):
    """
    A wrapper for schemaless Config.
    """
    def __init__(self, config, parent):
        self.config = config
        self.parent = parent
        #self.stateLookup = self.state_definitions
        #import pdb;pdb.set_trace()

    def __repr__(self):
        name = self.config.type
        if not name:
            name = 'main'
        return "<%s: %s>" % (self.__class__.__name__, name)

    def __getattr__(self, attr):
        attr = attr.replace('_', '-')
        val = None
        try:
            val = self.__dict__[attr]
        except KeyError:
            try:
                val = self.config[attr]
            except KeyError:
                val = self._getSection(attr)
        if isinstance(val, SchemalessSection):
            return val
        try:
            if val != None and len(val) == 1:
                val = val[0]
        except Exception, err:
            import pdb;pdb.set_trace()
        # check for boolean
        if isinstance(val, str):
            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
        return val

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

    def keys(self):
        return self.config.keys()
    getSectionAttributes = keys

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


class SchemalessConfig(BaseConfig, SchemalessSection):
    """
    A wrapper for schemaless ZConfig.
    """
    def __init__(self, config):
        self.config = config
        self.stateLookup = dict([
            (getattr(self.state_definitions, x), x)
            for x in self.state_definitions.keys()])

    def __getattr__(self, attr):
        return SchemalessSection.__getattr__(self, attr)

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


cfg = SchemalessConfig(config)


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

    def isMaintenance(self):
        if (
            self.app.checkForMaintenanceWindow(self.defaults) == True or
            self.app.checkForMaintenanceWindow(self.check) == True):
            return True
        return False

    def isDisabled(self):
        if (
            self.app.checkForDisabledService(self.defaults) == True or
            self.app.checkForDisabledService(self.check) == True):
            return True
        return False
