import os

from twisted.spread import pb
from twisted.spread.jelly import globalSecurity
from twisted.spread.flavors import IPBRoot
from twisted.internet import utils

from pymon.config import cfg
from pymon.utils.logger import log
from pymon.messaging import email
from pymon.messaging import message
from pymon.messaging import formatters

pb.setUnjellyableForClass(message.Message, message.ReceiverMessage)

class Listener(pb.Root):
    '''
    The listener is responsible for making connections to remote servers after
    receiving a message from pymon. As such (and in addition), the listener is
    a dispatcher for processing messages based on type.
    '''
    def remote_message(self, msgObj):
        '''
        Dispatch the appropriate message processor based on the message type.
        '''
        successMsg = ''

        def _cb(result, msg):
            log.info(msg)

        def _eb(err):
            log.error(err)

        if msgObj.type == 'email':
            d, successMsg = self.processEmail(msgObj)
        d.addCallback(_cb, successMsg)
        d.addErrback(_eb)
        return successMsg

    def processEmail(self, msgObj):
        '''
        # email kwds (to, from, subject) need to be set by the client;
        # ultimately, this data is set on the Message object that is
        # created in the workflow, and it is there that configuration
        # values will be used to populate this data.
        '''
        k = msgObj.kwds
        k['body'] = msgObj.content
        msg = formatters.email % k
        # XXX is it just gmail that is messing with the CRLFs?
        if k['to'].endswith('gmail.com'):
            msg = msg.replace('\r', '')
        successMsg = 'Email sent to %s.' % k['to']
        d = email.sendmail(
            cfg.smtp_username, cfg.smtp_password, cfg.mail_from, k['to'],
            msg, cfg.smtp_server, int(cfg.smtp_port))
        return (d, successMsg)

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

    def message(self, pbObj, msgObj):
        return pbObj.callRemote('message', msgObj)

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

