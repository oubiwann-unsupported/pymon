from twisted.python import components
from twisted.internet import task
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.interfaces import IState
from pymon.monitors.base import BaseMonitor
from pymon.utils.logger import log

from client import TCPSinglePingClient, TCPPingClient


class PingFactory(ClientFactory):

    protocol = TCPSinglePingClient

    def __init__(self):
        self.deferred = defer.Deferred()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)

    def clientConnectionLost(self, connector, reason):
        pass


class TCPPingMonitor(BaseMonitor):
    """
    The TCP ping monitor is a special case of monitor: it needs to perform
    *multiple* connects for a single check (as opposed to most monitors which
    connect only once to perforn a service check).

    As a result, we need a client factory which has a deferred and will errback
    when a connection fails.
    """
    protocol = TCPPingClient

    def __init__(self, uid, cfg):
        BaseMonitor.__init__(self, uid, cfg)
        self.ports = [int(x.strip()) for x in cfg.check.ports.split(',')]
        count = cfg.check.count or cfg.defaults.count or 1
        self.count = int(count)
        timeout = cfg.check.timeout or cfg.defaults.timeout or 1
        self.timeout = int(timeout)
        self.data = {
            'gain': {},
            'loss': {},
            'percent': {},
            'error': {}}

    def __call__(self):
        # call the superclass, but only to do the checks; don't connect, since
        # we need to iterate through the ports and connect several times per
        # port
        BaseMonitor.__call__(self, connect=False)
        for port in self.ports:
            d = self.doPing(port)
            d.addCallback(self.getPingReturn, port)
            d.addErrback(log.error)
            d.addCallback(self.protocol.connectionLost, 'completed ping')

    def doPing(self, port):
        # use the task cooperator to limit the number of connections
        # established to the same port to 1
        limiter = 1
        coop = task.Cooperator()
        def _doPing():
            for check in xrange(self.count):
                yield self.doFactory(port)
        ping = _doPing()
        pings = defer.DeferredList(
            [coop.coiterate(ping) for i in xrange(limiter)])
        return pings

    def doFactory(self, port):
        factory = PingFactory()
        reactor.connectTCP(self.host, port, factory, timeout=self.timeout)
        d = factory.deferred
        d.addCallback(self.recordConnection, port)
        d.addErrback(self.recordFailure, port)
        return d

    def recordConnection(self, result, port):
        self.data['gain'].setdefault(port, 0)
        self.data['gain'][port] += 1

    def recordFailure(self, failure, port):
        self.data['error'].setdefault(port, failure.getErrorMessage())
        self.data['loss'].setdefault(port, 0)
        self.data['loss'][port] += 1

    def getPingReturn(self, results, port):
        try:
            gain = self.data['gain'][port]
        except KeyError:
            gain = 0
        try:
            loss = self.data['loss'][port]
        except KeyError:
            loss = 0
        results = gain / (float(gain + loss) or 1)
        log.debug('Ping results: %s' % results)
        return results

components.registerAdapter(MonitorState, TCPPingMonitor, IState)
