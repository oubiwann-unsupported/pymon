from twisted.python import log
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
        status = int(self.factory.status)

        # push the returned data through the threshold checks
        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status, self.factory.message)
        self.rules.setSubj(checked_resource, status)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        log.msg('Service: %s' % self.factory.uid, debug=True)
        log.msg(self.rules.msg, debug=True)
        log.msg(self.rules.subj, debug=True)
        log.msg("Status: %s for %s" % (status, self.getHost()), debug=True)

        # update state information
        self.updateState()

        # dump info to log file
        log.msg(str(self.factory.state)+'\n', debug=True)

