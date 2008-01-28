from pymon.config import cfg
from pymon.utils import isInList, isInRange, isExactly
from pymon.utils.logger import log

class ThresholdRules(object):

    def __init__(self, factory):
        self.factory = factory
        self.setType(self.factory.cfg.defaults.threshold_type)
        self.messaging = MessagingRules(factory)

    def getOkThreshold(self):
        if self.factory.cfg.check.ok_threshold:
            return self.factory.cfg.check.ok_threshold
        else:
            return self.factory.cfg.defaults.ok_threshold

    def getWarnThreshold(self):
        if self.factory.cfg.check.warn_threshold:
            return self.factory.cfg.check.warn_threshold
        else:
            return self.factory.cfg.defaults.warn_threshold

    def getErrorThreshold(self):
        if self.factory.cfg.check.error_threshold:
            return self.factory.cfg.check.error_threshold
        else:
            return self.factory.cfg.defaults.error_threshold

    def getFailedThreshold(self):
        if self.factory.cfg.check.failed_threshold:
            return self.factory.cfg.check.failed_threshold
        else:
            return self.factory.cfg.defaults.failed_threshold

    def setType(self, type):
        self.threshold_type = type

    def check(self, datum):
        log.debug("Got check data '%s'." % datum)
        status = self.factory.cfg.app.state_definitions.unknown
        if self.isIn(datum, self.getOkThreshold()):
            log.debug("Status data is in 'ok' threshold.")
            status = self.factory.cfg.app.state_definitions.ok
            # The 'current status' index hasn't been updated yet, so
            # 'current status' is really 'last status', and 'last status'
            # is really the run prior to last.
            if self.factory.state.get('current status') not in (
                self.factory.cfg.app.state_definitions.ok,
                self.factory.cfg.app.state_definitions.recovering):
                status = self.factory.cfg.app.state_definitions.recovering
        elif self.isIn(datum, self.getWarnThreshold()):
            log.debug("Status data is in 'warn' threshold.")
            status = self.factory.cfg.app.state_definitions.warn
        elif self.isIn(datum, self.getErrorThreshold()):
            log.debug("Status data is in 'error' threshold.")
            status = self.factory.cfg.app.state_definitions.error
        elif self.isIn(datum, self.getFailedThreshold()):
            log.debug("Status data is in 'failed' threshold.")
            status = self.factory.cfg.app.state_definitions.failed
        elif datum == self.factory.cfg.app.state_definitions.failed:
            status = self.factory.cfg.app.state_definitions.failed
        return status

    def isIn(self, datum, threshold):
        '''
        Generic method for checking data against thresholds
        '''
        if self.threshold_type == 'ranged':
            isInFunc = isInRange
        elif self.threshold_type == 'listed':
            isInFunc = isInList
        elif self.threshold_type == 'exact':
            isInFunc = isExactly
        log.debug("Using method '%s'..." % isInFunc.func_name)
        log.debug("datum: %s" % datum)
        log.debug("datum type: %s" % type(datum))
        log.debug("threshold: %s" % threshold)
        log.debug("threshold type: %s" % type(threshold))
        return isInFunc(datum, threshold)

class MessagingRules(object):

    def __init__(self, factory):
        self.factory = factory
        self.messages = []

    # XXX what about escalation? Which messages are sent? How are
    # messages sent? When are they NOT sent? Who gets what?

    def isMessage(self, status):
        if status == self.factory.cfg.app.state_definitions.ok:
            return False
        return True

    def isEnabled(self):
        if self.factory.cfg.app.notifications.enabled:
            return True
        return False

    def isCutoff(self):
        cutoff = self.factory.cfg.app.notifications.cut_off
        if self.factory.state.get('count') > cutoff:
            log.info("Incident count has passed the cut-off " +
                "threshold; not sending email.")
            return True
        return False

    def isSend(self, status):
        if (self.isMessage(status) and self.isEnabled()
            and not self.isCutoff()):
            return True
        return False

    def createMessages(self, **kwds):
        '''
        For every type of enabled message, create a Message object that can be
        sent to the Listener.
        '''
        for type in self.factory.cfg.app.getEnabledNotificationTypes():
            print "Preparing to create message of type '%s' ..." % type
            # XXX uncomment this code and make it work
            #factory = MessageFactory(type, **kwds)
            #messages.append(factory.msg)

