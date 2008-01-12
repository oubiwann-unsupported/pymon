from twisted.python import components
from twisted.internet import task
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from pymon.utils.logger import log
from pymon.interfaces import IState
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.monitors import BaseMonitor

from client import TCPPingClient

class PingFactory(ClientFactory):

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

    def __call__(self):
        # call the superclass, but only to do the checks; don't connect, since
        # we need to iterate through the ports and connect several times per
        # port
        BaseMonitor.__call__(self, connect=False)
        for port in self.ports:
            d = self.doPing(port)
            d.addCallback(self.getPingReturn)
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
        self.ping = defer.DeferredList(
            [coop.coiterate(ping) for i in xrange(limiter)])

    def doFactory(self, port):
        factory = PingFactory()
        reactor.connectTCP(self.host, port, factory, timeout=self.timeout)
        d = factory.deferred
        d.addCallback(self.recordConnection, port)
        d.addErrback(self.recordFailure, port)

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

components.registerAdapter(MonitorState, TCPPingMonitor, IState)

