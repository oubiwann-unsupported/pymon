import os

from twisted.spread import pb
from twisted.spread.jelly import globalSecurity
from twisted.spread.flavors import IPBRoot
from twisted.internet import utils

class ProcessServer(pb.Root):
    '''
    This is the process agent for running processes, if you can believe
    that (sarcasm). It is an agent because this is how it will be used.

    Remote servers can run a twisted application that has this server as
    a service and receive connections over TCP, requesting methods to be
    run.

    A local instance of pymon can also run the agent server an a local
    client can be connected to it in order to run a local process and have
    all the benefits of using twisted factories/clients/servers.

    Note that the "remote_" is from the point of view of this perspective
    broker server and has nothing to do with pymon's perspective of
    "remote" or "local". If this process server runs on the local host,
    it will run the local binary, but to the perspective broker client,
    it will be remote.
    '''
    def remote_call(self, cmd, args):
        '''
        Execute a 'remote' binary.
        '''
        d = utils.getProcessOutput(cmd, args, env=os.environ, errortoo=1)
        return d

class ProcessServerFactory(pb.PBServerFactory):
    '''
    This is just a convenience wrapper for PBServerFactory.
    '''
    protocol = pb.Broker

    def __init__(self):
        self.root = IPBRoot(ProcessServer())
        self.unsafeTracebacks = False
        self.security = globalSecurity

class LocalAgentClient(pb.Broker):

    def connectionMade(self):
        pb.Broker.connectionMade(self)

class LocalAgentMonitor(pb.PBClientFactory):

    protocol = LocalAgentClient

    def __init__(self):
        pb.PBClientFactory.__init__(self)

    def __call__(self):
        return self.getRootObject()

    def clientConnectionLost(self, connector, reason, reconnecting=True):
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

