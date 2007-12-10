from datetime import datetime

from twisted.internet import protocol

from pymon import utils
from pymon.utils.logger import log
from pymon.config import cfg
from pymon.workflow.rules import ThresholdRules

class ClientMixin(object):

    def getHost(self):
        uri = utils.Uri(self.factory.uid)
        return uri.getAuthority().getHost()

    def buildRules(self):
        rules = ThresholdRules()
        rules.setType(self.factory.cfg.defaults.threshold_type)
        rules.factory = self.factory
        self.rules = rules

    def connectionMade(self):
        self.buildRules()

    def updateState(self):
        state = self.factory.state
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        uid = self.factory.uid

        prev = state.get('current status')
        org = self.factory.cfg.check.org
        if org:
            state.set('org', org)
        state.set('previous status', prev)
        state.set('previous status name', cfg.getStateNameFromNumber(prev))
        state.set('current status', self.rules.status)
        state.set('node', utils.getHostFromURI(uid))
        state.set('service', utils.getFriendlyTypeFromURI(uid))
        if state.get('previous status') == state.get('current status'):
            state.set('count', state.get('count') + 1)
        else:
            state.set('count', 1)
        status = self.rules.status
        #import pdb;pdb.set_trace()
        #if status == self.factory.cfg.app.state_definitions.recovering:
        #    status = self.factory.cfg.app.state_definitions.ok
        status = cfg.getStateNameFromNumber(status)
        try:
            state.set('desc', self.rules.msg)
        except AttributeError:
            # mo msg set
            pass
        state.set('current status name', status)
        state.set('last check', now)
        if status not in ['recovering', 'maintenance', 'disabled'
            'acknowledged']:
            count_index = 'count %s' % status
            state.set(count_index, state.get(count_index) + 1)
            state_index = 'last %s' % status
            state.set(state_index, now)

class NullClient(protocol.Protocol, ClientMixin):
    '''
    This is a client to be used when there is no actual connection to a
    service.
    '''
    factory = None

    def __init__(self):
        pass

    def __call__(self):
        pass

    def makeConnection(self, factory):
        '''
        This is the client "init()" method.
        '''
        self.factory = factory
        self.connected = None
        self.transport = None
        self.connectionMade()

    def connectionMade(self):
        '''
        We never got a connection, and therefore can't get a connection
        lost, so we need to do the things here that would normally get
        done in connectionLost.
        '''
        ClientMixin.connectionMade(self)
        log.debug("Factory in NullClient: %s" % self.factory)
        status = self.factory.cfg.app.state_definitions.failed
        checked_resource = self.factory.cfg.checks.uri
        log.debug("Starting rules processing...")
        self.rules.check(status)
        self.rules.setMsg(checked_resource, self.factory.status, self.factory.message)
        self.rules.setSubj(checked_resource)
        if self.rules.isSendMessage():
            self.rules.sendIt()
        log.debug("Finished rules processing.")

        # dump info to log file
        log.debug('NullClient Service: %s' % self.factory.uid)
        log.info(self.rules.msg)
        log.info(self.rules.subj)
        log.debug("NullClient Status: %s for %s" % (status, self.getHost()))

        # update state information
        self.updateState()

        # dump info to log file
        log.debug(self.factory.state)

