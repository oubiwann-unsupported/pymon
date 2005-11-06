from datetime import datetime

from twisted.internet import protocol

from adytum.util.uri import Uri
from pymon import utils

from rules import ThresholdRules

class ClientMixin(object):

    def getHost(self):
        uri = Uri(self.factory.uid)
        return uri.getAuthority().getHost()

    def buildRules(self):
        rules = ThresholdRules()
        rules.setType(self.factory.type_defaults.threshold_type)
        rules.factory = self.factory
        self.rules = rules

    def connectionMade(self):
        self.buildRules()

    def updateState(self):
        self.factory.state['last status'] = self.factory.state.get('current status')
        self.factory.state['current status'] = self.rules.status
        if self.factory.state['last status'] == self.factory.state['current status']:
            self.factory.state['count'] = self.factory.state['count'] + 1
        else:
            self.factory.state['count'] = 1
        status = self.rules.status
        if status == self.factory.statedefs.recovering:
            status = self.factory.statedefs.ok 
        status = utils.getStateNameFromNumber(status)
        state_index = 'last %s' % status
        self.factory.state[state_index] = datetime.now().strftime("%Y.%m.%d %H:%M:%S")


class NullClient(protocol.Protocol, ClientMixin):
    '''
    This is a client to be used when there is no actual 
    connection to a service.
    '''
    def __init__(self):
        pass
    
    def makeConnection(self):
        self.connected = None
        self.transport = None
        self.connectionMade()

    def connectionMade(self):
        ClientMixin.connectionMade(self)
        # we never got a connection, and therefore can't get
        # a connection lost, so we need to do the things here
        # that would normally get done in connectionLost.
        status = self.factory.statedefs.failed
        self.factory.message = "Cannot connect to server: connection failed."
        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, self.factory.status, self.factory.message)
        self.rules.setSubj(checked_resource)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        print 'Service: %s' % self.factory.uid
        print self.rules.msg 
        print self.rules.subj
        print "Status: %s for %s" % (status, self.getHost())

        # update state information
        self.updateState()

        # dump info to log file
        print self.factory.state
        print ''

