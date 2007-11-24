from email.MIMEText import MIMEText

from zope.interface import implements

from twisted.python import components
from twisted.spread import pb
from twisted.internet import reactor
from twisted.web.client import HTTPClientFactory
from twisted.web.client import PartialDownloadError
from twisted.internet.defer import TimeoutError
from twisted.internet.protocol import ClientFactory

from pymon import utils
from pymon.logger import log
from pymon.interfaces import IState
from pymon import application
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.clients.base import NullClient
from pymon.clients import ping, http, ftp, smtp, rules

class AbstractFactory(object):
    '''
    A class for generating a specific type of monitor, depending
    on the passed monitor type.

    The monitors are really client factories, and hold configuration
    and other data that the clients need or have use for.
    '''
    def __init__(self, serviceName, uri):

        self.uid = utils.makeUID(serviceName, uri)
        self.type = serviceName
        self.monitor = None

    def makeMonitor(self, cfg):
        '''
        Generic method for client creation.
        '''
        if self.type == 'ping':
            return self.makePingMonitor(cfg)
        if self.type == 'http_status':
            return self.makeHttpStatusMonitor(cfg)
        if self.type == 'http_text':
            return self.makeHttpTextMonitor(cfg)
        if self.type == 'ftp':
            return self.makeFtpMonitorMonitor(cfg)
        if self.type == 'smtp_status':
            return self.makeSmtpStatusMonitor(cfg)
        if self.type == 'smtp_mail':
            return self.makeSmtpMailMonitor(cfg)

    def makePingMonitor(self, cfg):
        monitor = PingMonitor(self.uid, cfg)
        return monitor

    def makeHttpStatusMonitor(self, cfg):
        monitor = HttpStatusMonitor(self.uid, cfg)
        return monitor

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

class HttpTextMonitor(HTTPClientFactory, BaseMonitor):
    
    def __init__(self, uid):
        BaseMonitor.__init__(self, uid, cfg)
        self.page_url = ''
        self.text_check = ''
        self.reactor_params = ()
        self.checkdata = self.service.entries.entry(uri=self.uid)

class HttpStatusMonitor(HTTPClientFactory, BaseMonitor):
    
    protocol = http.HttpStatusClient

    def __init__(self, uid, cfg):
        BaseMonitor.__init__(self, uid, cfg)
        self.page_url = 'http://%s' % self.checkConfig.uri
        # XXX write a getTimeout method
        #timeout = self.checkConfig.timeout
        #timeout = self.defaults.timeout
        self.agent = cfg.user_agent_string
        self.method = 'HEAD'
        self.status = None
        # XXX write a method to get the http port from defaults or service config
        #port = self.checkConfig.http_port
        port = self.defaults.remote_port
        self.reactor_params = (self.host, port, self)

    def __repr__(self):
        """
        We need to override the __repr__ in HTTPClientFactory; 
        inheriting from BaseMonitor won't do it.
        """
        return "<%s: %s>" % (self.__class__.__name__, self.uid)

    def __call__(self):
        HTTPClientFactory.__init__(self, self.page_url,
            method=self.method, agent=self.agent,
            timeout=self.defaults.interval)
        BaseMonitor.__call__(self)
        # this deferred is created above when 
        # HTTPClientFactory.__init__() is called.
        d = self.deferred
        d.addCallback(self.logStatus)
        d.addErrback(self.errorHandlerPartialPage)
        d.addErrback(self.errorHandlerTimeout)

    def clientConnectionFailed(self, connector, reason):
        self.message = reason.getErrorMessage()
        log.error("Failed: %s" % self.message)
        self._setupNullClient()

    def logStatus(self):
        log.info('Return status: %s' % self.status)
        self.message = "test message: ",self.status

    def errorHandlerPartialPage(self, failure):
        failure.trap(PartialDownloadError)
        log.error("Hmmm... got a partial page...")
        log.debug('Return status: %s' % self.status)

    def errorHandlerTimeout(self, failure):
        failure.trap(TimeoutError)
        self.message = failure.getErrorMessage()
        log.error("Timeout: %s" % self.message)
        self._setupNullClient()
    
    def _setupNullClient(self):
        '''
        This needs to be called anytime we didn't get a connection. 
        Rules processing occurs 
        '''
        self.status = '0'
        log.debug('Entered null client setup...')
        self.original_protocol = self.protocol
        log.debug('Original Protocol: %s' % self.original_protocol)
        self.protocol = NullClient()
        log.debug('New Protocol: %s' % self.protocol)
        self.protocol.makeConnection(self)
        self.protocol = self.original_protocol
        log.debug('Reverted Protocol: %s' % self.protocol)

components.registerAdapter(MonitorState, HttpStatusMonitor, IState)

class PingMonitor(pb.PBClientFactory, BaseMonitor):

    protocol = ping.PingClient

    def __init__(self, uid, cfg):
        pb.PBClientFactory.__init__(self)
        BaseMonitor.__init__(self, uid, cfg)

        # ping config options setup
        self.checkdata = self.cfg

        # get the info in order to make the next ping
        self.binary = self.defaults.binary
        count = '-c %s' % self.defaults.count
        self.args = [count, self.host]

        #options = ['ping', '-c %s' % count, '%s' % self.host]
        port = cfg.agents.port
        self.reactor_params = ('127.0.0.1', port, self)

    def __call__(self):
        BaseMonitor.__call__(self)
        d = self.getRootObject()
        d.addCallback(self.pingHost)
        d.addCallback(self.getPingReturn)

    def pingHost(self, pbobject):
        return pbobject.callRemote('call', self.binary, self.args)

    def getPingReturn(self, results):
        self.data = results
        #print dir(self)
        log.debug('Ping results: %s' % results)
        self.disconnect()

    def clientConnectionLost(self, connector, reason, reconnecting=1):
        """Reconnecting subclasses should call with reconnecting=1."""
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

components.registerAdapter(MonitorState, PingMonitor, IState)
