from twisted.spread import pb
from twisted.internet.protocol import Protocol

from pymon.logger import log
from pymon.clients.base import ClientMixin


class PingClient(Protocol, ClientMixin):

    def connectionMade(self):
        self.factory.deferred.callback("success")
        self.transport.loseConnection()
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):
        results = self.factory.data
        log.debug(results)
        # XXX this needs to be done in workflow
        self.rules.check(results['gain'])
        self.rules.setMsg(results['gain'], self.getHost())
        self.rules.setSubj(self.getHost(), results['loss'])
        if self.rules.isSendMessage():
            self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("Status: %s for %s" % (self.rules.status, host))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug('State Data: '+str(self.factory.state.data)+'\n')


class LocalAgentPingClient(pb.Broker, ClientMixin):

    def connectionMade(self):
        pb.Broker.connectionMade(self)
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):

        from pymon.pingparser import OutputParser

        # parse returned data
        log.debug(self.factory.data)
        parse = OutputParser(self.factory.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()
        host = self.getHost()

        # push the returned data through the threshold checks
        self.rules.check(gain)
        self.rules.setMsg(gain, host)
        self.rules.setSubj(host, loss)
        if self.rules.isSendMessage():
            self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("Status: %s for %s" % (self.rules.status, host))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug('State Data: '+str(self.factory.state.data)+'\n')
