from twisted.protocols.ftp import FTPClient, FTPFactory
from twisted.application import service, internet
from twisted.internet import defer, reactor
from twisted.internet.protocol import ClientFactory 

INTERVAL = 60

##################
# CLIENT SECTION #
##################
class FtpClient(FTPClient):

    def connectionMade(self):
        FTPClient.__init__(self, self.factory.username,
                           self.factory.password, self.factory.passive)
        print "Connected to FTP server '%s'..." % self.factory.host

    def connectionLost(self, reason):
        print "FTP Status code after disconnect: %s" % self.return_code

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
        self.return_code = code
        print 'Line: %s' % line
        #print 'Rsponse: %s' % self.response
        print 'Code: %s' % code
        self.quit()
        self.sendNextCommand()
        

###################
# MONITOR SECTION #
###################
class Monitor(ClientFactory):

    protocol = FtpClient

    def __init__(self):
        self.host = 'ftp.mozilla.org'
        self.port = 21
        self.username = 'annonymous'
        self.password = 'pymon@adytum.us'
        self.passive = 1

    def __call__(self):
        reactor.connectTCP(self.host, self.port, self)
    
#######################
# APPLICATION SECTION #
#######################
application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

##################
# ENGINE SECTION #
##################
monitor = Monitor()
server = internet.TimerService(INTERVAL, monitor)
server.setServiceParent(pymonServices)
