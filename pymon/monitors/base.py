import sys

from twisted.internet import reactor

from pymon import application
from pymon import utils
from pymon.application import MonitorState, globalRegistry
from pymon.clients import NullClient
from pymon.interfaces import IState
from pymon.utils.logger import log


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
        dottedName = '%s.%s' % (self.type.replace('-', '_'), subMod)
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
        self.message = None
        self.setInterval()
        self.reactorArgs = ()
        self.reactorKwds = {}

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.uid)

    def __call__(self, connect=True):
        self.updateState()
        if not (self.isMaintenance() or self.isDisabled()):
            # we always want the maintenance and disabled checks to run, even
            # if we're not connecting (right away)
            if connect:
                reactor.connectTCP(*self.reactorArgs, **self.reactorKwds)

    def __getstate__(self):
        return self.__dict__

    def _setNonCheckState(self, nonCheckState, msg):
            log.warning(msg)
            self.state = application.setNonChangingState(self.state,
                nonCheckState, self.uid)
            globalRegistry.factories[self.uid].state = self.state

    def updateState(self):
        # update the configuration in case it has changed
        # XXX not sure if state stuff is doing what we expect it to be doing...
        IState(self).save()
        self.state = IState(self)

    def isMaintenance(self):
        if self.cfg.isMaintenance():
            msg = "Service %s has been disabled during maintenance."
            stateID = self.cfg.app.state_definitions.maintenance
            self._setNonCheckState(stateID, msg % self.uid)
            return True
        return False

    def isDisabled(self):
        if self.cfg.isDisabled():
            msg = "Service %s has been disabled; not checking."
            stateID = self.cfg.app.state_definitions.disabled
            self._setNonCheckState(stateID, msg % self.uid)
            return True
        return False

    def host(self):
        return utils.getHostFromURI(self.uid)
    host = property(host)

    def setInterval(self, seconds=None):
        #import pdb;pdb.set_trace()
        def useDef():
            interval = self.cfg.defaults.interval
            log.debug('Set interval from service check defaults')
            return interval
        if seconds:
            interval = seconds
            log.debug('Manually set interval')
        else:
            interval = self.cfg.check.interval
            if interval:
                log.debug('Set interval from service check config')
            else:
                interval = useDef()
        if not interval:
            interval = useDef()
        self._interval = int(interval)

    def getInterval(self):
        return self._interval

    interval = property(getInterval, setInterval)
