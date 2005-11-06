from twisted.spread import pb

from adytum.app.pymon.registry import globalRegistry
from adytum.app.pymon import utils

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
        print 'Service: %s' % self.factory.uid
        print self.rules.msg 
        print self.rules.subj
        print 'Status: %s' % self.rules.status

        # update state information
        self.updateState()

        # dump info to log file
        print self.factory.state
        print ''

