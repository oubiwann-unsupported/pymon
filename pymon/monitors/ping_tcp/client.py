from twisted.internet.protocol import Protocol

from pymon.clients import ClientMixin
from pymon.utils.logger import log


class TCPSinglePingClient(Protocol):

    def connectionMade(self):
        self.factory.deferred.callback("success")
        self.transport.loseConnection()


class TCPPingClient(Protocol, ClientMixin):

    def connectionMade(self):
        self.factory.deferred.callback("success")
        self.transport.loseConnection()
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):
        results = self.factory.data
        log.debug(results)

        # push the returned data through the threshold checks
        status = self.rules.check(gain)
        self.workflow.checkTransition(status, self.factory.cfg)
        #self.rules.setMsg(results['gain'], self.getHost())
        #self.rules.setSubj(self.getHost(), results['loss'])
        #if self.rules.isSendMessage():
        #    self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.debug("Status: %s for %s" % (self.rules.status, host))

        # update state information
        self.updateState()

        # dump info to log file
        log.info('State Data: '+str(self.factory.state.data)+'\n')

        # final cleanup
        ClientMixin.connectionLost(self)
