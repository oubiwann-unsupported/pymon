from twisted.web.error import Error
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.mail.smtp import SMTPClient

import StringIO

INTERVAL = 10

##################
# CLIENT SECTION #
##################
class SmtpClient(SMTPClient):

    mail_from = 'pymon@adytum.us'
    mail_to =  'rbhalotia@innovetech.com'
    mail_data = '''\
                From: pymon@adytum.us
                To: rbhalotia@innovetech.com
                Subject: Tutorate!

                Hello, how are you, goodbye.
                '''
 
    def getMailFrom(self):
        result = self.mail_from
        self.mail_from = None
        return result

    def getMailTo(self):
        return [self.mail_to]

    def getMailData(self):
        return StringIO.StringIO(self.mail_data)

    def sentMail(self, code, resp, numOk, addresses, log):
        print 'Sent: code %s' % code, numOk, 'messages'
        self._disconnectFromServer()

    def connectionLost(self, reason):
        print "Disconnected from the server: %s " % reason

###################
# MONITOR SECTION #
###################
class Monitor(ClientFactory):

    protocol = SmtpClient

    def __init__(self):
        self.host = 'localhost1'
        self.port = 25
        self.identity = 'innovetech.com'

    def buildProtocol(self, addr):
        return self.protocol(identity=self.identity, logsize=10)

    def __call__(self):
        reactor.connectTCP(self.host, self.port, self)

    def clientConnectionFailed(self, connector, reason):
        print "Connection Failed: %s " % reason

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
