from twisted.python import components

from pymon.utils.logger import log
from pymon.interfaces import IState
from pymon.monitors import BaseMonitor
from pymon.application import MonitorState
from pymon.application import globalRegistry
from pymon.agents.local import LocalAgentMonitor

from client import LocalAgentPingClient

class LocalAgentPingMonitor(LocalAgentMonitor, BaseMonitor):

    protocol = LocalAgentPingClient

    def __init__(self, uid, cfg):
        LocalAgentMonitor.__init__(self)
        BaseMonitor.__init__(self, uid, cfg)

        # get the info in order to make the next ping
        self.binary = self.cfg.defaults.binary
        count = '-c %s' % self.cfg.defaults.count
        self.args = [count, self.host]
        port = int(cfg.app.agents.local_command.port)
        self.reactorArgs = ('127.0.0.1', port, self)

    def __call__(self):
        BaseMonitor.__call__(self)
        d = LocalAgentMonitor.__call__(self)
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

components.registerAdapter(MonitorState, LocalAgentPingMonitor, IState)

