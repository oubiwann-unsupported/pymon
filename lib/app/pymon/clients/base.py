from datetime import datetime

from adytum.util.uri import Uri
from adytum.app.pymon import utils

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
        state_index = 'last %s' % utils.getStateNameFromNumber(self.rules.status)
        self.factory.state[state_index] = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

