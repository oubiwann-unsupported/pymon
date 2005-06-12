from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error
from twisted.internet import utils
from twisted.internet import defer

from adytum.util.striphtml import StrippingParser
from adytum.net.ping import OutputParser

##################
# process server #
##################
class ProcessServer(Protocol):
    def connectionMade(self):
        self.transport.write('connected...\r\n')
        output = utils.getProcessOutput(self.factory.binary, self.factory.args)
        output.addCallbacks(self.writeResponse, self.noResponse)
    def writeResponse(self, resp):
        p = OutputParser(resp)
        msg = 'Ping check: there was a %s%% loss and %s%% gain from %s.\r\n' 
        msg = msg % (p.getPingLoss(), p.getPingGain(), self.factory.pinghost)
        self.transport.write(msg)
        self.transport.write('losing connection...')
        self.transport.loseConnection()
    def noResponse(self, err):
        self.transport.write('got error: %s' % err)
        self.transport.write('losing connection...')
        self.transport.loseConnection()
    
class PingServerFactory(Factory):
    protocol = ProcessServer
    def __init__(self):
        # this would access globalRegistry
        self.binary = '/sbin/ping'
        self.pinghost = '127.0.0.1'
        self.args = ['-c 4', self.pinghost]

class ProcessClient(Protocol):
    def connectionMade(self):
        self.data = ''
    def dataReceived(self, data):
        self.data += data
    def connectionLost(self, reason):
        print self.data

class PingClientFactory(Factory):
    protocol = ProcessClient
    def __init__(self):
        self.deferred = defer.Deferred()
    def startedConnecting(self, a): pass
    def clientConnectionLost(self, a, b): pass
        
INTERVAL = 10

################
# main section #
################
def pingCallback(contents, factory):
    print 'contents: %s' % contents
    print 'factory: %s' % factory

def runMonitors(factory):
    reactor.connectTCP('127.0.0.1', 10999, factory)
    d = factory.deferred
    d.addCallback(pingCallback, factory)

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

ping_factory = PingClientFactory()
server = internet.TimerService(INTERVAL, runMonitors, ping_factory)
server.setServiceParent(pymonServices)

factory = PingServerFactory()
server = internet.TCPServer(10999, factory)
server.setServiceParent(pymonServices)
