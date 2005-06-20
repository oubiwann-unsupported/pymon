import commands
from random import random

from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.web.client import HTTPPageGetter, HTTPClientFactory, PartialDownloadError
from twisted.web.error import Error
from twisted.internet import utils
from twisted.internet import defer
from twisted.spread import pb

from adytum.util.striphtml import StrippingParser
from adytum.net.ping import OutputParser

##################
# spread process #
##################
class ProcessServer(pb.Root):
    def remote_ping(self, args):
        '''
	    Note that the "remote_" is from the point of view of
	    this perspective broker server and has nothing to do
	    with pymon's perspective of "remote" or "local". If
	    this process server runs on the local host, it will run
	    the local ping binary, but to the perspective broker
	    client, it will be remote.
        '''
        command = '/sbin/ping'
        d = utils.getProcessOutput(command, args)
        return d

    def remote_uptime(self):
        command = '/usr/bin/uptime\r\n'
        d = utils.getProcessOutput(command)
        return d

    def remote_echo(self, text):
        command = '/bin/echo'
        d = utils.getProcessOutput(command, [text+'\r\n'])
        return d

class ProcessClientFactory(pb.PBClientFactory):
    def __init__(self):
        pb.PBClientFactory.__init__(self)
        self.state = {}
        self.history = {}

def pingHost(pbobject):
    args = ['-c 5', 'www.yahoo.com']
    #args = ['-c 4', 'www.adytumsolutions.com']
    return pbobject.callRemote('ping', args)

def getPingReturn(results, factory):
    p = OutputParser(results)
    msg = 'Ping check: there was a %s%% loss and %s%% gain from %s.'
    msg = msg % (p.getPingLoss(), p.getPingGain(), p.getHostname())
    # play with facotry state machine 
    factory.state.setdefault('this',  None)
    factory.state.setdefault('last',  None)
    factory.history.setdefault('last_message',  None)
    factory.state['this'] = random()
    # now see the difference between last state and this state
    print 'service state: %s' % factory.state
    print 'service history: %s' % factory.history
    factory.state['last'] = factory.state['this']
    factory.history['last_message'] = msg
    # send back actual ping results 
    print msg

def simpleCall(pbobject, call, params):
    return pbobject.callRemote(call, params)

def simpleReturn(results, factory):
    return results
    
INTERVAL = 10

################
# main section #
################
def runMonitors(factory):
    reactor.connectTCP('127.0.0.1', 10999, factory)
    #d = factory.getRootObject()
    #d.addCallback(pingHost)
    #d.addCallback(getPingReturn, factory)
    d = factory.getRootObject()
    d.addCallback(simpleCall, 'echo', 'this text is echoed')
    d.addCallback(simpleReturn, factory)

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

pbclient_factory = ProcessClientFactory()
server = internet.TimerService(INTERVAL, runMonitors, pbclient_factory)
server.setServiceParent(pymonServices)

factory = pb.PBServerFactory(ProcessServer())
server = internet.TCPServer(10999, factory)
server.setServiceParent(pymonServices)
