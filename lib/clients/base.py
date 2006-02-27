from datetime import datetime

from twisted.internet import protocol

from adytum.util.uri import Uri

from pymon import utils
from pymon.logger import log
from pymon.config import cfg

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
        state = self.factory.state
        now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        uri = Uri(self.factory.uid)
        
        prev = state.get('current status')
        org = self.factory.service_cfg.org
        if org:
            state['org'] = org
        state['previous status'] = prev
        state['previous status name'] = utils.getStateNameFromNumber(prev)
        state['current status'] = self.rules.status
        state['node'] = uri.getAuthority().getHost()
        state['service'] = uri.getScheme().replace('_', ' ')
        if state['previous status'] == state['current status']:
            state['count'] = state['count'] + 1
        else:
            state['count'] = 1
        status = self.rules.status
        #if status == self.factory.statedefs.recovering:
        #    status = self.factory.statedefs.ok 
        status = utils.getStateNameFromNumber(status)
        try:
            state['desc'] = self.rules.msg
        except AttributeError:
            # mo msg set
            pass
        state['current status name'] = status
        state['last check'] = now
        if status not in ['recovering', 'maintenance', 'disabled'
            'acknowledged']:
            count_index = 'count %s' % status
            state[count_index] = state[count_index] + 1
            state_index = 'last %s' % status
            state[state_index] = now

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
        self.service_cfg = self.factory.service_cfg
        status = self.factory.statedefs.failed
        checked_resource = self.factory.service_cfg.uri
        log.debug("Starting rules processing...")
        self.rules.check(status)
        self.rules.setMsg(checked_resource, self.factory.status, self.factory.message)
        self.rules.setSubj(checked_resource)
        if self.rules.isMessage():
            if cfg.notifications.enabled:
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

