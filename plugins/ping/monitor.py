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

        # ping config options setup
        self.checkdata = self.cfg

        # get the info in order to make the next ping
        self.binary = self.defaults.binary
        count = '-c %s' % self.defaults.count
        self.args = [count, self.host]

        #options = ['ping', '-c %s' % count, '%s' % self.host]
        port = int(cfg.agents.port)
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
        """
        Reconnecting subclasses should call with reconnecting=1.
        """
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

components.registerAdapter(MonitorState, LocalAgentPingMonitor, IState)

