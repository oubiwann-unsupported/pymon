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
    p = StrippingParser()
    p.valid_tags = tuple()
    p.feed(contents)
    p.close()
    p.cleanup()
    contents = p.result.replace('\n', ' ')
    print 'Here are the contents: %s' % contents
    print 'Here is dir(param): %s' % dir(param)
    print 'Here is headers: %s' % param.headers
    print 'Here is response_headers: %s' % param.response_headers
    print 'Here is status: %s' % param.status
    print 'Here is protocol: %s' % param.protocol
    #print 'Here is param.deferred: %s' % param.deferred
    #print 'Here is dir(param.deferred): %s' % dir(param.deferred)

def errorHandlerPartialPage(failure, param):
    failure.trap(PartialDownloadError)
    print "Hmmm... got a partial page..."
    print 'Here is status: %s' % param.status

def errorHandler(failure, param):
    failure.trap(Error)
    print "There was an error..."
    print 'Here is status: %s' % param.status

def runMonitors(factory):
    #deferred = getPage('http://www.google.com/index.html', method='GET', agent=agent)
    #deferred.addCallback(printCallback)
    reactor.connectTCP('localhost', 80, factory)
    d = factory.deferred
    d.addCallback(printCallback, factory)
    d.addErrback(errorHandlerPartialPage, factory)
    d.addErrback(errorHandler, factory)

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

agent = 'pymon 0.2.1'
#factory = HTTPClientFactory('http://localhost/index.html', method='HEAD', agent=agent, timeout=4)
http_factory = HTTPClientFactory('http://www.google.com/', method='HEAD', agent=agent, timeout=10)

server = internet.TimerService(INTERVAL, runMonitors, http_factory)
server.setServiceParent(pymonServices)
