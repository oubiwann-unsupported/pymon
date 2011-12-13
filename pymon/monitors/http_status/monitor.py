from twisted.internet.defer import TimeoutError
from twisted.python import components
from twisted.web.client import HTTPClientFactory
from twisted.web.client import PartialDownloadError

from pymon.application import MonitorState
from pymon.clients import NullClient
from pymon.interfaces import IState
from pymon.monitors.base import BaseMonitor
from pymon.utils.logger import log

from client import HttpStatusClient


class HttpStatusMonitor(HTTPClientFactory, BaseMonitor):

    protocol = HttpStatusClient

    def __init__(self, uid, cfg):
        BaseMonitor.__init__(self, uid, cfg)
        self.page_url = 'http://%s' % self.checkConfig.uri
        # XXX write a getTimeout method
        #timeout = self.checkConfig.timeout
        #timeout = self.defaults.timeout
        self.agent = cfg.user_agent_string
        self.method = 'HEAD'
        self.status = None
        # XXX write a method to get the http port from defaults or service
        # config
        #port = self.checkConfig.http_port
        #import pdb;pdb.set_trace()
        port = int(self.defaults.remote_port)
        self.reactorArgs = (self.host, port, self)

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
