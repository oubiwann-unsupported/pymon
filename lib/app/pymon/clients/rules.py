import dispatch

from adytum.app.pymon import utils

class ThresholdRules(object):
    # XXX need checks for state and separate checks for
    # notification
    # XXX generalize threshold checks here... how much of this
    # really should be in workflow?
    # XXX what about escalation? Which messages are sent? How are
    # messages sent? When are they NOT sent? Who gets what?

    def getOkThreshold(self):
        if self.factory.service_cfg.ok.threshold:
            return self.factory.service_cfg.ok.threshold
        else:
            return self.factory.type_defaults.ok.threshold

    def getWarnThreshold(self):
        if self.factory.service_cfg.warn.threshold:
            return self.factory.service_cfg.warn.threshold
        else:
            return self.factory.type_defaults.warn.threshold

    def getErrorThreshold(self):
        if self.factory.service_cfg.error.threshold:
            return self.factory.service_cfg.error.threshold
        else:
            return self.factory.type_defaults.error.threshold

    def setType(self, type):
        self.threshold_type = type

    def check(self, datum):
        if self.isIn(datum, self.getOkThreshold()):
            status = self.factory.statedefs.ok
            # The 'current status' index hasn't been updated yet, so 
            # 'current status' is really 'last status', and 'last status'
            # is really the run prior to last.
            if self.factory.state.get('current status') not in (self.factory.statedefs.ok,
                self.factory.statedefs.recovering):
                status = self.factory.statedefs.recovering
            self.status = status
        elif self.isIn(datum, self.getWarnThreshold()):
            self.status = self.factory.statedefs.warn
        elif self.isIn(datum, self.getErrorThreshold()):
            self.status = self.factory.statedefs.error
        elif datum == self.factory.statedefs.failed:
            self.status = self.factory.statedefs.failed
        else:
            self.status = self.factory.statedefs.unknown

    [ dispatch.generic() ]
    def isIn(self, datum, threshold):
        '''
        Generic method for testing threshold
        '''

    [ isIn.when("self.threshold_type == 'ranged'") ]
    def rangedIsIn(self, datum, threshold):
        return utils.isInRange(datum, threshold)

    [ isIn.when("self.threshold_type == 'listed'") ]
    def listedIsIn(self, datum, threshold):
        return utils.isInList(datum, threshold)

    [ isIn.when("self.threshold_type == 'exact'") ]
    def isExactly(self, datum, threshold):
        if str(datum) == threshold:
            return True
        return False

    def isMessage(self):
        if self.status == self.factory.statedefs.ok:
            return False
        return True

    def setMsg(self, *args):
        self.msg = self.factory.type_defaults.message_template % args

    def setSubj(self, *args):
        status = utils.getStateNameFromNumber(self.status)
        msg = self.factory.type_defaults.get(status).get('message')
        self.subj = msg % args

    def sendIt(self):
        from adytum.app.pymon.message import LocalMail

        if self.status == self.factory.statedefs.recovering:
            self.msg = self.msg + '\r\nRecovering from state %s.' % self.factory.state.get('current status')
        cfg = self.factory.service_cfg
        sendmail = self.factory.mailcfg.sendmail
        frm = self.factory.mailcfg.from_address
        # XXX we probably want to make the actual sending of emails
        # non-blocking. Dererreds anyone?
        # XXX modify this when support for escalation and different 
        # group levels is added to python
        for address in utils.getMailList(self.factory.uid):
            email = LocalMail()
            email.setSendmailBinary(sendmail)
            email.setSubject(self.subj)
            email.setTo(address)
            email.setFrom(frm)
            email.setData(self.msg)
            email.send()
            print self.factory.type_defaults.sent_message % address  

