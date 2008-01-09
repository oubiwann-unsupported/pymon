from twisted.python import components
from twisted.spread import pb
from twisted.internet.protocol import ClientFactory

from pymon.utils.logger import log
from pymon.interfaces import IState
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.monitors import BaseMonitor

from client import LocalAgentPingClient

class LocalAgentPingMonitor(pb.PBClientFactory, BaseMonitor):

    protocol = LocalAgentPingClient

    def __init__(self, uid, cfg):
        pb.PBClientFactory.__init__(self)
        BaseMonitor.__init__(self, uid, cfg)

        # get the info in order to make the next ping
        self.binary = self.cfg.defaults.binary
        count = '-c %s' % self.cfg.defaults.count
        self.args = [count, self.host]
        port = int(cfg.app.agents.port)
        self.reactorArgs = ('127.0.0.1', port, self)

    def __call__(self):
        BaseMonitor.__call__(self)
        d = self.getRootObject()
        d.addCallback(self.pingHost)
        d.addErrback(log.error)
        d.addCallback(self.getPingReturn)
        d.addErrback(log.error)

    def pingHost(self, pbobject):
        return pbobject.callRemote('call', self.binary, self.args)

    def getPingReturn(self, results):
        self.data = results
        log.debug('Ping results: %s' % results)
        self.disconnect()

    def clientConnectionLost(self, connector, reason, reconnecting=True):
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

components.registerAdapter(MonitorState, LocalAgentPingMonitor, IState)

