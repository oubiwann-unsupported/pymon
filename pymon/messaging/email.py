import sys
from StringIO import StringIO
from OpenSSL.SSL import SSLv3_METHOD

from twisted.mail.smtp import ESMTPSenderFactory
from twisted.python.usage import Options, UsageError
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from pymon.config import cfg
from pymon.utils import isInList, isInRange, isExactly
from pymon.utils.logger import log

def sendmail(username, password, fromAddress, toAddress, message, smtpHost,
             smtpPort=25):
    """
    @param username: The username with which to authenticate.
    @param password: The password with which to authenticate.
    @param fromAddress: The SMTP reverse path (ie, MAIL FROM)
    @param toAddress: The SMTP forward path (ie, RCPT TO)
    @param message: text containing the headers and body of the message to send.
    @param smtpHost: The MX host to which to connect.
    @param smtpPort: The port number to which to connect.

    @return: A Deferred which will be called back when the message has been
    sent or which will errback if it cannot be sent.
    """
    # Create a context factory which only allows SSLv3 and does not verify
    # the peer's certificate.
    contextFactory = ClientContextFactory()
    contextFactory.method = SSLv3_METHOD
    d = Deferred()
    senderFactory = ESMTPSenderFactory(
        username,
        password,
        fromAddress,
        toAddress,
        StringIO(message),
        d,
        contextFactory=contextFactory)
    reactor.connectTCP(smtpHost, smtpPort, senderFactory)
    return d

class LocalMail(object):

    def setSendmailBinary(self, bin='/usr/sbin/sendmail'):
        self.sendmail = bin

    def send(self):
        import os
        self._prepMessage()
        p = os.popen("%s -t" % self.sendmail, "w")
        p.write(self.mail_data)
        sts = p.close()
        #return sts
        #if sts != 0:
        #    print "Sendmail exit status", sts

class RemoteMail(object):

    def setHost(self, host):
        self.host = host

    def send(self):
        import smtplib
        self._prepMessage()
        mail=smtplib.SMTP(self.host)
        mail.sendmail(self.frm,self.to,self.mail_data)
        mail.close()

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

