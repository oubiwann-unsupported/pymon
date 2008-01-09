from twisted.python import components
from twisted.internet import defer
from twisted.internet.protocol import ClientFactory

from pymon.utils.logger import log
from pymon.interfaces import IState
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.monitors import BaseMonitor

from client import TCPPingClient

class TCPPingMonitor(ClientFactory, BaseMonitor):

    protocol = TCPPingClient

    def __init__(self, uid, cfg):
        BaseMonitor.__init__(self, uid, cfg)
        self.ports = [int(x.strip()) for x in cfg.check.ports.split(',')]
        self.count = cfg.check.count or cfg.defaults.count

    def __call__(self):
        for port in self.ports:
            dl = []
            for check in xrange(self.count):
                self.reactorArgs = (self.host, port, self)
                BaseMonitor.__call__(self)
                d = defer.Deferred()
                d.addCallback(self.recordConnection, port)
                d.addErrback(self.recordFailure, port)
                dl.append(d)
            dl = DeferredList(dl)
            dl.addCallback(self.getPingReturn, port)
            dl.addErrback(log.error)

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)

    def clientConnectionLost(self, connector, reason):
        pass

    def recordConnection(self, result, port):
        self.data['success'].setdefault(port, 0)
        self.data['success']['port'] += 1

    def recordFailure(self, failure, port):
        portData = self.data['failure'].setdefault(host, [])
        data = (port, failure.getErrorMessage())
        portData.append(data)

    def getPingReturn(self, results, port):
        self.data = results
        log.debug('Ping results: %s' % results)
        self.disconnect()

    def clientConnectionLost(self, connector, reason, reconnecting=1):
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

components.registerAdapter(MonitorState, LocalAgentPingMonitor, IState)

