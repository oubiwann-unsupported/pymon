from twisted.spread import pb
from twisted.internet.protocol import Protocol

from pymon.utils.logger import log
from pymon.clients import ClientMixin
from pymon.utils.pingparser import OutputParser


class LocalAgentPingClient(pb.Broker, ClientMixin):

    def connectionMade(self):
        pb.Broker.connectionMade(self)
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):
        # parse returned data
        log.debug(self.factory.data)
        parse = OutputParser(self.factory.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()
        host = self.getHost()

        # push the returned data through the threshold checks
        status = self.rules.check(gain)
        self.workflow.checkTransition(status, self.factory.cfg)
        #self.rules.setMsg(gain, host)
        #self.rules.setSubj(host, loss)
        #if self.rules.isSendMessage():
        #    self.rules.sendIt()

        # update state information
        self.updateState()

        # dump info to log file
        log.info('State Data: '+str(self.factory.state.data)+'\n')

        # final cleanup
        ClientMixin.connectionLost(self)


