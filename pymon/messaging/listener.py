import os

from twisted.spread import pb
from twisted.spread.jelly import globalSecurity
from twisted.spread.flavors import IPBRoot
from twisted.internet import utils

from pymon.utils.logger import log

class Listener(pb.Root):
    '''
    The listener is responsible for making connections to remote servers after
    receiving a message from pymon. As such (and in addition), the listener is
    an intelligent client factory, more or less.
    '''
    def remote_message(self, msgType, msgContent, svcHost, svcType, **kwds):
        '''
        Dispatch the appropriate message processor based on the message type.
        '''
        data = (msgType, msgContent, svcHost, svcType, kwds)
        print data
        return data
        #d = utils.getProcessOutput(cmd, args, env=os.environ, errortoo=1)
        #return d

class ListenerFactory(pb.PBServerFactory):
    '''
    This is a convenience wrapper for PBServerFactory with a defined root
    attribute being a Listener instance.
    '''
    protocol = pb.Broker

    def __init__(self):
        self.root = IPBRoot(Listener())
        self.unsafeTracebacks = False
        self.security = globalSecurity

class ListenerClient(pb.PBClientFactory):

    protocol = pb.Broker

    def __init__(self):
        pb.PBClientFactory.__init__(self)

    def message(self, pbObj, msgObj):
        return pbObj.callRemote(
            'message', msgObj.type, msgObj.content, msgObj.host,
            msgObj.service, **msgObj.kwds)

    def send(self, msgObj):
        d = self.getRootObject()
        d.addCallback(self.message, msgObj)
        d.addErrback(log.error)
        d.addCallback(log.info)
        return d

    def clientConnectionLost(self, connector, reason, reconnecting=True):
        if reconnecting:
            # any pending requests will go to next connection attempt
            # so we don't fail them.
            self._broker = None
            self._root = None
        else:
            self._failAll(reason)

def _test():

    host = '127.0.0.1'
    port = 10001

    def startServer():
        from twisted.internet import reactor
        reactor.listenTCP(port, ListenerFactory())
        reactor.run()

    def sendMessage():
        from twisted.internet import reactor
        from pymon.messaging.message import Message
        # create a message
        msg = Message(type='echo', content='testing...')
        msg.kwds = {'to': 'test@test.com', 'from': 'pymon@test.com', 'subject':
                    'test message'}
        # create a client instance and connect to the listener
        client = ListenerClient()
        reactor.connectTCP(host, port, client)
        # pass the message and shut the listener down afterwards
        d = client.send(msg)
        d.addCallback(reactor.stop)
        reactor.run()

    startServer()
    sendMessage()

if __name__ == '__main__':
    _test()
