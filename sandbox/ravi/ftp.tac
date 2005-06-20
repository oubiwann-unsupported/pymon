from twisted.protocols.ftp import FTPClient, FTPFactory
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory 

INTERVAL = 10

##################
# CLIENT SECTION #
##################
class ftpClient(FTPClient):

    def connectionMade(self):
        FTPClient.__init__(self, self.factory.username,
                           self.factory.password, self.factory.passive)
        print "connection made"
        self.quit()
        print "connection disconnected"

    def connectionLost(self, reason):
        print "Connection lost; status: %s" % reason 

    def lineReceived(self, line):
        print line

###################
# MONITOR SECTION #
###################
class Monitor(ClientFactory):

    protocol = ftpClient

    def __init__(self):
        self.host = 'localhost'
        self.port = 21
        self.username = 'test'
        self.password = 'test'
        self.passive = 1

    def __call__(self):
        reactor.connectTCP(self.host, self.port, self)

    def clientConnectionLost(self, connector, reason):
        print "connection lost:", reason

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason

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
