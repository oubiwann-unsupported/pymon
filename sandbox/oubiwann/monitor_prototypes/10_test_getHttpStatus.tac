from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol
from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error

from adytum.util.striphtml import StrippingParser

INTERVAL = 10

class Client(HTTPPageGetter):
    def connectionLost(self, reason):
        print "Connection lost; status: %s" % self.factory.status

class Monitor(HTTPClientFactory):

    protocol = Client

    def __init__(self):
        agent = 'pymon 0.2.1'
        self.host = 'www.google.com'
        url = 'http://%s/'%self.host
        HTTPClientFactory.__init__(self, url, method='HEAD', agent=agent, timeout=10) 

    def __call__(self):
        reactor.connectTCP(self.host, 80, self)
        d = self.deferred
        d.addCallback(self.printCallback)
        d.addErrback(self.errorHandlerPartialPage)
        d.addErrback(self.errorHandler)

    def printCallback(self, contents):
        print 'Here is status: %s' % self.status

    def errorHandlerPartialPage(self, failure):
        failure.trap(PartialDownloadError)
        print "Hmmm... got a partial page..."
        print 'Here is status: %s' % self.status

    def errorHandler(self, failure):
        failure.trap(Error)
        print "There was an error..."
        print 'Here is status: %s' % self.status

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)
monitor = Monitor()
server = internet.TimerService(INTERVAL, monitor)
server.setServiceParent(pymonServices)
