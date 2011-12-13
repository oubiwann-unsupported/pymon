from twisted.internet.protocol import Protocol

from pymon.agents.local import LocalAgentClient
from pymon.clients import ClientMixin
from pymon.utils.pingparser import OutputParser
from pymon.utils.logger import log


class LocalAgentPingClient(LocalAgentClient, ClientMixin):

    def connectionMade(self):
        LocalAgentClient.connectionMade(self)
        ClientMixin.setup(self)

    def processRules(self, checkData, **kwds):
        """
        Push the returned data through the threshold checks and create any
        needed messages for notification, which will be send by the
        workflow's doTrans() method (if messaging is enabled).
        """
        status = self.rules.check(checkData)
        if self.rules.messaging.isSend(status):
            self.rules.messaging.createMessages(**kwds)
        self.workflow.checkTransition(status, self.factory.cfg, self.rules)
        #self.rules.setMsg(gain, host)
        #self.rules.setSubj(host, loss)

    def connectionLost(self, reason):
        # parse returned data
        log.debug(self.factory.data)
        parse = OutputParser(self.factory.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()
        host = self.getHost()

        # threshold checks, messaging, and workflow
        self.processRules(gain, host=host, loss=loss, gain=gain)

        # update state information
        self.updateState()

        # dump info to log file
        log.info('State Data: '+str(self.factory.state.data)+'\n')

        # final cleanup
        LocalAgentClient.connectionLost(self, reason)
        ClientMixin.teardown(self)
