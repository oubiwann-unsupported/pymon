from twisted.web.client import HTTPPageGetter
from twisted.web.http import HTTPClient

from base import ClientMixin

class HttpTextClient:

    def connectionLost(self, reason):
        pass
    
class HttpStatusClient(HTTPPageGetter, ClientMixin):

    def connectionMade(self):
        HTTPPageGetter.connectionMade(self)
        ClientMixin.connectionMade(self)
    
    def connectionLost(self, reason):
        status = self.factory.status
        host = self.getHost()

        # push the returned data through the threshold checks
        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status)
        self.rules.setSubj(checked_resource, checked_resource)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        print 'Service: %s' % self.factory.uid
        print self.rules.msg 
        print self.rules.subj
        print "Status: %s for %s" % (status, host)

        # update state information
        self.updateState()

        # dump info to log file
        print self.factory.state
        print ''

