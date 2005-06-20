import commands

from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error
from twisted.internet import utils
from twisted.internet import defer
from twisted.spread import pb

from adytum.app.pymon import agents
from adytum.util.striphtml import StrippingParser
from adytum.net.ping import OutputParser

##################
# spread process #
##################
def pingHost(pbobject):
    args = ['-c 5', 'www.yahoo.com']
    #args = ['-c 4', 'www.adytumsolutions.com']
    return pbobject.callRemote('call', '/sbin/ping', args)

def getPingReturn(results):
    p = OutputParser(results)
    msg = 'Ping check: there was a %s%% loss and %s%% gain from %s.'
    msg = msg % (p.getPingLoss(), p.getPingGain(), p.getHostname())
    print msg

def uptimeHost(pbobject):
    return pbobject.callRemote('call', '/usr/bin/uptime', [])

def getUptimeReturn(results):
    print 'Uptime check: %s' % results.strip()
    
INTERVAL = 10

################
# main section #
################
def runMonitors(factory):
    reactor.connectTCP('127.0.0.1', 10999, factory)
    d = factory.getRootObject()
    d.addCallback(pingHost)
    d.addCallback(getPingReturn)
    d = factory.getRootObject()
    d.addCallback(uptimeHost)
    d.addCallback(getUptimeReturn)

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

pbclient_factory = pb.PBClientFactory()
server = internet.TimerService(INTERVAL, runMonitors, pbclient_factory)
server.setServiceParent(pymonServices)

factory = agents.ProcessServerFactory()
server = internet.TCPServer(10999, factory)
server.setServiceParent(pymonServices)
