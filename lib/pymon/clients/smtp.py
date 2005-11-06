from twisted.mail.smtp import SMTPClient
from base import ClientMixin
import StringIO

class SmtpMailClient(SMTPClient, ClientMixin):

    def connectionMade(self):
        ClientMixin.connectionMade(self)
        print "Connected to SMTP server '%s'..." % self.factory.host
        self.setTimeout(self.timeout)
        self._expected = [ 220 ]
        self._okresponse = self.smtpState_helo
        self._failresponse = self.smtpConnectionFailed
        print "Response from server : %s" % self._expected

    def getMailFrom(self):
        result = self.factory.mail_from
        self.factory.mail_from = None
        return result

    def getMailTo(self):
        return [self.factory.mail_to]

    def getMailData(self):
        return StringIO.StringIO(self.factory.mail_data)

    def sentMail(self, code, resp, numOk, addresses, log):
        print 'Sent: code %s' % code, numOk, 'messages'
        self.factory.status = code
        self._disconnectFromServer()

    def connectionLost(self, reason):
        print "Disconnected from the server: %s " % reason
        status = self.factory.status

        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status, "")
        self.rules.setSubj(checked_resource, checked_resource)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        print 'Service: %s' % self.factory.uid
        print self.rules.msg
        print self.rules.subj
        print "Status: %s for %s" % (status, self.factory.host)

        # update state information
        self.updateState()

        # dump info to log file
        print self.factory.state
        print ''



class SmtpStatusClient(SMTPClient, ClientMixin):

    def connectionMade(self):
        ClientMixin.connectionMade(self)
        print "Connected to SMTP server '%s'..." % self.factory.host
        self.setTimeout(self.timeout)
        self._expected = [ 220 ]
        self._okresponse = self.smtpState_helo
        self._failresponse = self.smtpConnectionFailed
        if (self._okresponse):
            self.factory.status = '220'
        else:
            self.factory.status = '111'

        self._disconnectFromServer()

    def connectionLost(self, reason):
        print "Disconnected from the server: %s " % reason
        status = self.factory.status

        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status, "")
        self.rules.setSubj(checked_resource, checked_resource)
        if self.rules.isMessage():
            self.rules.sendIt()

        # dump info to log file
        print 'Service: %s' % self.factory.uid
        print self.rules.msg
        print self.rules.subj
        print "Status: %s for %s" % (status, self.factory.host)

        # update state information
        self.updateState()

        # dump info to log file
        print self.factory.state
        print ''


