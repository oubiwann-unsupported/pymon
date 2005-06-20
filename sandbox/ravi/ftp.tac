from twisted.protocols.ftp import FTPClient
from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory 

INTERVAL = 60

##################
# CLIENT SECTION #
##################
class ftpClient(FTPClient):

    def connectionMade(self):
        self.__init__(self.factory.username,
                      self.factory.password, self.factory.passive)
    def pwd(self):
        """
        print working directory method for ftp client
        """

    def quit(self):
        """
        disconnect from the server
        """

    def connectionLost(self, reason):
        print "Connection lost; status: %s" % reason 

    def lineReceived(self, line):
        code = line[0:3]
        print code

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
        self.passive = 0

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
