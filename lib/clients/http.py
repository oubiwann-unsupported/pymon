from twisted.web.client import HTTPPageGetter
from twisted.web.http import HTTPClient

from base import ClientMixin

from pymon.registry import globalRegistry
from pymon import utils
from pymon.utils import log

class HttpTextClient:

    def connectionLost(self, reason):
        pass
    
class HttpStatusClient(HTTPPageGetter, ClientMixin):

    def connectionMade(self):
        HTTPPageGetter.connectionMade(self)
        ClientMixin.connectionMade(self)
    
    def connectionLost(self, reason):
        status = int(self.factory.status)
        checked_resource = self.factory.service_cfg.uri

        # push the returned data through the threshold checks
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status, self.factory.message)
        self.rules.setSubj(checked_resource, status)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("Status: %s for %s" % (status, self.getHost()))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug(str(self.factory.state)+'\n')

