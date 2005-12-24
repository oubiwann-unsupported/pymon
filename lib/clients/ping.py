from twisted.spread import pb

from pymon.registry import globalRegistry
from pymon import utils
from pymon.utils import log

from base import ClientMixin

class PingClient(pb.Broker, ClientMixin):

    def connectionMade(self):
        pb.Broker.connectionMade(self)
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):

        from adytum.net.ping import OutputParser
        
        # parse returned data
        parse = OutputParser(self.factory.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()
        host = self.getHost()

 
        # push the returned data through the threshold checks
        self.rules.check(gain)
        self.rules.setMsg(gain, host)
        self.rules.setSubj(host, loss)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("Status: %s for %s" % (self.rules.status, host))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug(str(self.factory.state)+'\n')

