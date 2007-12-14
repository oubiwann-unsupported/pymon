from pymon.config import cfg
from pymon.utils.logger import log

def rangedIsIn(datum, threshold):
    log.debug("Using method 'rangedIsIn'...")
    log.debug("datum: %s" % datum)
    log.debug("datum type: %s" % type(datum))
    log.debug("threshold: %s" % threshold)
    log.debug("threshold type: %s" % type(threshold))
    threshold = [int(x) for x in threshold.split('-')]
    threshold[1] += 1
    if datum in xrange(*threshold):
        return True
    else:
        return False

def listedIsIn(datum, threshold):
    log.debug("Using method 'listedIsIn'...")
    if datum in threshold:
        return True
    return False

def isExactly(datum, threshold):
    log.debug("Using method 'isExactly'...")
    if str(datum) == threshold:
        return True
    return False

class ThresholdRules(object):

    def __init__(self, factory):
        self.factory = factory
        self.setType(self.factory.cfg.defaults.threshold_type)

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
            return rangedIsIn(datum, threshold)
        elif self.threshold_type == 'listed':
            return listedIsIn(datum, threshold)
        elif self.threshold_type == 'exact':
            return isExactly(datum, threshold)

class AsYetUndterminedClassName(object):
    # XXX define me!

    # XXX what about escalation? Which messages are sent? How are
    # messages sent? When are they NOT sent? Who gets what?
    def isMessage(self):
        if self.status == self.factory.cfg.app.state_definitions.ok:
            return False
        return True

    def msgEnabled(self):
        if self.factory.cfg.notifications.enabled:
            return True
        return False

    def cutOffReached(self):
        cutoff = self.factory.cfg.notifications.cut_off
        if self.factory.state.get('count') > cutoff:
            log.info("Incident count has passed the cut-off " + \
                "threshold; not sending email.")
            return True
        return False

    def isSendMessage(self):
        if (self.isMessage and self.msgEnabled
            and not self.cutOffReached):
            return True
        return False

    def setMsg(self, *args):
        self.msg = self.factory.cfg.defaults.message_template % args

    def setSubj(self, *args):
        status = cfg.getStateNameFromNumber(self.status)
        if status == 'unknown':
            self.subj = "Unknown status"
        else:
            msg = getattr(self.factory.cfg.defaults, '%s_message' % status)
            # XXX This try/except is a quick hack that REALLY needs to
            # be done right... just because it's so ugly... and...
            # ugly.
            try:
                self.subj = msg % args
            except TypeError:
                # for "not all arguments converted during string
                # formatting"
                self.subj = msg % args[0]

    def sendIt(self):
        from pymon.message import LocalMail

        if self.status == self.factory.cfg.app.state_definitions.recovering:
            status_id = self.factory.state.get('current status')
            status = cfg.getStateNameFromNumber(status_id)
            self.msg = self.msg + "\r\nRecovering from '%s'." % status
        sendmail = self.factory.cfg.sendmail
        frm = self.factory.cfg.mail_from
        # XXX we probably want to make the actual sending of emails
        # non-blocking. Dererreds anyone?
        # XXX modify this when support for escalation and different
        # group levels is added to python
        for address in cfg.getMailList(self.factory.uid):
            email = LocalMail()
            email.setSendmailBinary(sendmail)
            email.setSubject(self.subj)
            email.setTo(address)
            email.setFrom(frm)
            email.setData(self.msg)
            email.send()
            log.info(self.factory.cfg.defaults.sent_message % address)

