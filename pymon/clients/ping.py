from twisted.spread import pb

from pymon import utils
from pymon.logger import log

from base import ClientMixin

class PingClient(pb.Broker, ClientMixin):

    def connectionMade(self):
        pb.Broker.connectionMade(self)
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):

        from adytum.net.ping import OutputParser
        
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
