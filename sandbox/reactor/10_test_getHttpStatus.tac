from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol
from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error

from adytum.util.striphtml import StrippingParser

INTERVAL = 10

################
# main section #
################
def printCallback(contents, param):
    print 'Here is status: %s' % param.status

def errorHandlerPartialPage(failure, param):
    failure.trap(PartialDownloadError)
    print "Hmmm... got a partial page..."
    print 'Here is status: %s' % param.status

def errorHandler(failure, param):
    failure.trap(Error)
    print "There was an error..."
    print 'Here is status: %s' % param.status

class Protocol(HTTPPageGetter):
    def connectionLost(self, reason):
        print "Connection lost; status: %s" % self.factory.status

class Monitor(HTTPClientFactory):

    protocol = Protocol

    def __init__(self):
        agent = 'pymon 0.2.1'
        self.host = 'www.google.com'
        HTTPClientFactory.__init__(self, 'http://%s/'%self.host, method='HEAD', agent=agent, timeout=10) 

    def __call__(self):
        reactor.connectTCP(self.host, 80, self)
        d = self.deferred
        d.addCallback(printCallback, self)
        d.addErrback(errorHandlerPartialPage, self)
        d.addErrback(errorHandler, self)

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)
monitor = Monitor()
server = internet.TimerService(INTERVAL, monitor)
server.setServiceParent(pymonServices)
