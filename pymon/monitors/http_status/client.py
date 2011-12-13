from twisted.web.client import HTTPPageGetter

from pymon.clients import ClientMixin
from pymon.utils.logger import log
from pymon.workflow import rules


class HttpStatusClient(HTTPPageGetter, ClientMixin):

    def connectionMade(self):
        HTTPPageGetter.connectionMade(self)
        ClientMixin.connectionMade(self)

    def connectionLost(self, reason):
        status = self.factory.status
        if status:
            status = int(status)
        log.debug(str(dir(self.factory)))
        log.debug(str(self.factory.headers))
        log.debug(str(self.factory.response_headers))
        checked_resource = self.factory.checkConfig.uri

        # push the returned data through the threshold checks
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status, self.factory.message)
        self.rules.setSubj(checked_resource, status)
        if self.rules.isSendMessage():
            self.rules.sendIt()

        # dump info to log file
        log.debug('Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("Status: %s for %s" % (status, self.getHost()))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug('State Data: '+str(self.factory.state.data)+'\n')

