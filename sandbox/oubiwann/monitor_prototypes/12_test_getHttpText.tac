from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error
from twisted.application import service, internet
from twisted.internet import reactor

from adytum.util.striphtml import StrippingParser

INTERVAL = 10

##################
# CLIENT SECTION #
##################
# no client for this; using HTTPPageGetter

###################
# MONITOR SECTION #
###################
class Monitor(HTTPClientFactory):

    def __init__(self):
        self.agent = 'pymon 0.2.1'
        self.host = 'www.google.com'
        self.url = 'http://%s/'%self.host
        self.search_text = 'About Google&copy;2005'
        self.bad_text = 'badness'

    def __call__(self):
        HTTPClientFactory.__init__(self, self.url, agent=self.agent, timeout=10) 
        reactor.connectTCP(self.host, 80, self)
        d = self.deferred
        d.addCallback(self.printCallback)
        d.addErrback(self.errorHandlerPartialPage)
        d.addErrback(self.errorHandler)

    def printCallback(self, contents):
        print 'Here is status: %s' % self.status
        p = StrippingParser()
        p.valid_tags = tuple()
        p.feed(contents)
        p.close()
        p.cleanup()
        contents = p.result.replace('\n', ' ')
        print 'Here are the contents: %s' % contents
        print 'Good: %s' % contents.find(self.search_text)
        print 'Bad: %s' % contents.find(self.bad_text)

    def errorHandlerPartialPage(self, failure):
        failure.trap(PartialDownloadError)
        print "Hmmm... got a partial page..."
        print 'Here is status: %s' % self.status

    def errorHandler(self, failure):
        failure.trap(Error)
        print "There was an error..."
        print 'Here is status: %s' % self.status

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
