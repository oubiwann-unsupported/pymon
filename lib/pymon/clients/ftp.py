from twisted.protocols.ftp import FTPClient
from base import ClientMixin

class FtpStatusClient(FTPClient, ClientMixin):

    def connectionMade(self):
        self.__init__(self.factory.username,
                      self.factory.password, self.factory.passive)
        ClientMixin.connectionMade(self)
        print "Connected to FTP server '%s'..." % self.factory.host
   

    def lineReceived(self, line):
        self.response.append(line)
        try:
            code = line[0:3]
        except IndexError:
            return

        # Bail out if this isn't the last line of a response
        # The last line of response starts with 3 digits followed by a space
        codeIsValid = len(filter(lambda c: c in '0123456789', code)) == 3
        if not (codeIsValid and line[3] == ' '):
            return

        # Ignore marks
        if code[0] == '1':
            return
        self.factory.return_code = code
        print 'Line: %s' % line
        print 'Code: %s' % code
        self.quit()
        self.sendNextCommand()


    def connectionLost(self, reason):
        print "FTP Status code after disconnect: %s" % self.factory.return_code
        status = self.factory.return_code

        checked_resource = self.factory.service_cfg.uri
        self.rules.check(status)
        self.rules.setMsg(checked_resource, status)
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
