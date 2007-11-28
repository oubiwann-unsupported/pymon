import os
import pwd, grp
from itertools import chain
from StringIO import StringIO
from datetime import datetime

from ZConfig.schemaless import loadConfigFile

from pymon.utils import getTypeFromURI

def getConfigFiles():
    confs = chain(os.walk('etc/services'), os.walk('plugins'))
    for base, dirs, files in confs:
        if not files:
            continue
        for name in files:
            if name.endswith('.conf'):
                yield "%s/%s" % (base, name)

def assembleConfig_old():
    fh = open("etc/pymon.conf")
    data = fh.read() + '<services>'
    fh.close()
    for path in getConfigFiles():
        fh = open(path)
        data += fh.read()
        fh.close()
    data += '</services>'
    configFile = StringIO(data)
    print configFile.getvalue()
    return configFile

# we need to iterate through the files and keep track of their opening tags so
# that we can group services together under their own tags
def assembleConfig():
    # first, let's gather all the data so that we can sort by tag name
    data = []
    for path in getConfigFiles():
        fh = open(path)
        raw = fh.read()
        fh.close()
        tag = raw.split('\n')[0].strip()
        tag = tag.replace('<', '').replace('>', '')
        if tag:
            data.append((tag, raw))
    data.sort()
    # next we need to group service configs according to type
    wrapped = {}
    for tag, data in dict(data).items():
        container = '-'.join(tag.split('-')[:-1])
        wrapped.setdefault(container, '')
        wrapped[container] += data
    # now let's assemble the thing
    fh = open("etc/pymon.conf")
    conf = fh.read() + '<services>\n'
    fh.close()
    for tag, data in wrapped.items():
        group = ''
        for item in data:
            group += item
        conf += '<%s>\n%s\n</%s>\n' % (tag, group, tag)
    conf += '\n</services>'
    configFile = StringIO(conf)
    return configFile

config = loadConfigFile(assembleConfig())
#import pdb;pdb.set_trace()

def refreshConfig():
    log.info("Checking for config file changes...")
    conf_file = utils.getResource(['etc', 'pymon.conf'])
    conf = open(conf_file).read()
    new_md5 = md5.new(conf).hexdigest()
    old_md5 = globalRegistry.state.get('config_md5')
    globalRegistry.state['config_md5'] = new_md5
    # check against MD5 in state
    if new_md5 != old_md5:
        log.warning("Config MD5 signatures do not match; loading new config...")
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
        return val

    def _getSection(self, name):
        #name = name.replace('-', '_')
        for section in self.config.sections:
            if section.type == name:
                #return section
                return SchemalessSection(section, name)

    def keys(self):
        return self.config.keys()

class SchemalessConfig(BaseConfig):
    """
    A wrapper for schemaless ZConfig.
    """
    def __init__(self, config):
        self.config = config
        #self.stateLookup = self.state_definitions
        #import pdb;pdb.set_trace()
        self.stateLookup = dict([
            (getattr(self.state_definitions, x), x)
            for x in self.state_definitions.keys()])

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
        return val

    def _getSection(self, name):
        #name = name.replace('-', '_')
        for section in self.config.sections:
            if section.type == name:
                #return section
                s = SchemalessSection(section, name)
                return s

    def getEnabledNames(self):
        '''
        Convenience function for the list of service types that are
        enabled.
        '''
        # XXX this is ugly and wrong... replacing characters like this
        # shouldn't happen at this level. This should be enforced elsewhere.
        return [ x.replace(' ', '_') for x in self.monitor_status.enable ]

    def getEnabledServices(self):
        '''
        A set-powered means of geting the services.
        '''
        enabled = set(self.getEnabledNames())
        pymonServices = set(self.services.keys())
        return enabled.intersection(pymonServices)


cfg = SchemalessConfig(config)

