import sys

from twisted.internet import reactor

from pymon import utils
from pymon.utils.logger import log
from pymon.interfaces import IState
from pymon import application
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.clients import NullClient

sys.path.append('./plugins')

class AbstractFactory(object):
    '''
    A class for generating a specific type of monitor, depending
    on the passed monitor type.

    The monitors are really client factories, and hold configuration
    and other data that the clients need or have use for.
    '''
    def __init__(self, factoryName, serviceName, uri):

        self.uid = utils.makeUID(serviceName, uri)
        self.type = serviceName
        self.monitor = None
        self.factoryName = factoryName

    def getMonitorClass(self):
        subMod = 'monitor'
        dottedName = '%s.%s' % (self.type, subMod)
        plugin = __import__(dottedName)
        monitor = getattr(plugin, subMod)
        return getattr(monitor, self.factoryName)

    def makeMonitor(self, cfg):
        '''
        Generic method for client creation.
        '''
        return self.getMonitorClass()(self.uid, cfg)


class BaseMonitor(object):

    def __init__(self, uid, cfg):
        self.uid = uid
        self.cfg = cfg
        self.interval = None
        self.message = None
        self.host = utils.getHostFromURI(self.uid)
        self.checkConfig = cfg.getCheckConfigFromURI(self.uid)
        self.defaults = cfg.getDefaultsFromURI(self.uid)
        self.stateDefs = cfg.state_definitions
        self.setInterval()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.uid)

    def __call__(self):
        # update the configuration in case it has changed
        IState(self).save()
        self.state = IState(self)
        if self.cfg.checkForMaintenanceWindow(self.checkConfig):
            # XXX These two chunks of state info access need to be moved
            # out of here... and made less eyesoreingly redundant.
            # There's another set of XXX's that discuss this in general
            # elsewhere. There are also notes in the TODO.
            msg = "Service %s has been disabled during maintenance."
            log.warning(msg % self.uid)
            self.state = application.setNonChangingState(self.state,
                self.stateDefs.maintenance, self.uid)
            globalRegistry.factories[self.uid].state = self.state
        elif self.checkConfig.enabled:
            reactor.connectTCP(*self.reactor_params)
        else:
            msg = "Service %s has been disabled; not checking."
            log.warning(msg % self.uid)
            self.state = application.setNonChangingState(self.state,
                self.stateDefs.disabled, self.uid)
            globalRegistry.factories[self.uid].state = self.state

    def __getstate__(self):
        return self.__dict__

    def setInterval(self, seconds=None):
        def useDef():
            interval = self.defaults.interval
            log.debug('Set interval from service check defaults')
            return interval
        if seconds:
            interval = seconds
            log.debug('Manually set interval')
        else:
            try:
                interval = self.checkConfig.interval
                if interval:
                    log.debug('Set interval from service check config')
            except AttributeError:
                interval = useDef()
        if not interval:
            interval = useDef()
        self.interval = interval

    def getInterval(self):
        return self.interval
