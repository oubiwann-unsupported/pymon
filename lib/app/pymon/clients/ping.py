from twisted.spread import pb

from adytum.app.pymon.registry import globalRegistry
from adytum.app.pymon import utils
from base import ClientMixin

class PingClient(pb.Broker, ClientMixin):

    def connectionMade(self):
        pb.Broker.connectionMade(self)

    def connectionLost(self, reason):

        from adytum.net.ping import OutputParser
        
        parse = OutputParser(self.factory.data)
        loss = parse.getPingLoss()
        gain = parse.getPingGain()
        host = self.getHost()
        msg = self.getMsg() % (gain, host)

        # XXX a full list of these needs to be defined and initialized in
        # the monitors (client factories) and not done here.
        # XXX we also don't want to have to refer to things via list
        # indicides.
        self.factory.state.setdefault('last status', -1)
        self.factory.state.setdefault('current status', -1)
        print self.factory.state

        # XXX generalize threshold checks here... how much of this
        # really should be in workflow?
	    # XXX what about escalation? Which messages are sent? How are
        # messages sent? When are they NOT sent? Who gets what?
        if utils.isInRange(gain, self.getOkThreshold()):
            status = self.factory.statedefs.ok
            # these haven't been reset yet, so 'current status' is really
            # 'current status'
            if self.factory.state['current status'] in (self.factory.statedefs.ok,
                self.factory.statedefs.recovering):
                subj = 'pymon OK: %s : %s%% loss' % (host, loss)
            else:
                status = self.factory.statedefs.recovering
                subj = 'pymon RECOVERING: %s : %s%% loss' % (host, loss)
                msg = msg + '\r\nRecovering from state %s.' % self.factory.state['current status']
        elif utils.isInRange(gain, self.getWarnThreshold()):
            status = self.factory.statedefs.warn
            subj = 'pymon WARNING: %s : %s%% loss' % (host, loss)
        elif utils.isInRange(gain, self.getErrorThreshold()):
            status = self.factory.statedefs.error
            subj = 'pymon ERROR: %s : %s%% loss' % (host, loss)
        else:
            status = self.factory.statedefs.unknown
        print 'Service: %s' % self.factory.uid
        print msg
        print subj
        print 'status = %s' % status
        self.factory.state['last status'] = self.factory.state['current status']
        self.factory.state['current status'] = status
        print self.factory.state
        print ''
        if status in (self.factory.statedefs.warn,
            self.factory.statedefs.error,
            self.factory.statedefs.recovering):
            from adytum.app.pymon.message import LocalMail
            cfg = self.factory.service_cfg
            sendmail = self.factory.mailcfg.sendmail
            frm = self.factory.mailcfg.from_address
            # we probably want to make the actual sending of emails
            # non-blocking. Dererreds anyone?
            for address in cfg.escalation.group(level='0').maillist.email:
                email = LocalMail()
                email.setSendmailBinary(sendmail)
                email.setSubject(subj)
                email.setTo(address)
                email.setFrom(frm)
                email.setData(msg)
                email.send()
                print "Sent ping notice email message to %s" % address  
