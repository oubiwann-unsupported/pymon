from pymon.config import cfg
from pymon.logger import log

class ThresholdRules(object):
    # XXX need checks for state and separate checks for
    # notification
    # XXX generalize threshold checks here... how much of this
    # really should be in workflow?
    # XXX what about escalation? Which messages are sent? How are
    # messages sent? When are they NOT sent? Who gets what?

    def getOkThreshold(self):
        if self.factory.checkConfig.ok_threshold:
            return self.factory.checkConfig.ok_threshold
        else:
            return self.factory.defaults.ok_threshold

    def getWarnThreshold(self):
        if self.factory.checkConfig.warn_threshold:
            return self.factory.checkConfig.warn_threshold
        else:
            return self.factory.defaults.warn_threshold

    def getErrorThreshold(self):
        if self.factory.checkConfig.error_threshold:
            return self.factory.checkConfig.error_threshold
        else:
            return self.factory.defaults.error_threshold

    def getFailedThreshold(self):
        if self.factory.checkConfig.failed_threshold:
            return self.factory.checkConfig.failed_threshold
        else:
            return self.factory.defaults.failed_threshold

    def setType(self, type):
        self.threshold_type = type

    def check(self, datum):
        log.debug("Got check data '%s'." % datum)
        if self.isIn(datum, self.getOkThreshold()):
            log.debug("Status data is in 'ok' threshold.")
            status = self.factory.stateDefs.ok
            # The 'current status' index hasn't been updated yet, so 
            # 'current status' is really 'last status', and 'last status'
            # is really the run prior to last.
            if self.factory.state.get('current status') not in (
                self.factory.stateDefs.ok,
                self.factory.stateDefs.recovering):
                status = self.factory.stateDefs.recovering
            self.status = status
        elif self.isIn(datum, self.getWarnThreshold()):
            log.debug("Status data is in 'warn' threshold.")
            self.status = self.factory.stateDefs.warn
        elif self.isIn(datum, self.getErrorThreshold()):
            log.debug("Status data is in 'error' threshold.")
            self.status = self.factory.stateDefs.error
        elif self.isIn(datum, self.getFailedThreshold()):
            log.debug("Status data is in 'failed' threshold.")
            self.status = self.factory.stateDefs.failed
        elif datum == self.factory.stateDefs.failed:
            self.status = self.factory.stateDefs.failed
        else:
            self.status = self.factory.stateDefs.unknown

    def isIn(self, datum, threshold):
        '''
        Generic method for checking data against thresholds
        '''
        if self.threshold_type == 'ranged':
            self.rangedIsIn(datum, threshold)
        elif self.threshold_type == 'listed':
            self.listedIsIn(datum, threshold)
        elif self.threshold_type == 'exact':
            self.isExactly(datum, threshold)

    def rangedIsIn(self, datum, threshold):
        log.debug("Using method 'rangedIsIn'...")
        log.debug("datum: %s" % datum)
        log.debug("datum type: %s" % type(datum))
        log.debug("threshold: %s" % threshold)
        log.debug("threshold type: %s" % type(threshold))
        if datum in threshold:
            return True
        else:
            return False

    def listedIsIn(self, datum, threshold):
        log.debug("Using method 'listedIsIn'...")
        if datum in threshold:
            return True
        return False

    def isExactly(self, datum, threshold):
        log.debug("Using method 'isExactly'...")
        if str(datum) == threshold:
            return True
        return False

    def isMessage(self):
        if self.status == self.factory.stateDefs.ok:
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
        self.msg = self.factory.defaults.message_template % args

    def setSubj(self, *args):
        status = cfg.getStateNameFromNumber(self.status)
        if status == 'unknown':
            self.subj = "Unknown status"
        else:
            msg = getattr(self.factory.defaults, '%s_message' % status)
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
        
        if self.status == self.factory.stateDefs.recovering:
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
            log.info(self.factory.defaults.sent_message % address)

