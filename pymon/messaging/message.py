from twisted.spread import pb

class RawMessage(object):
    '''
    A convenience object for general pymon messages representing human-readable
    content and metadata for such things as state changes.
    '''
    def __init__(self, type='', content='', host='localhost', service='ping',
                 kwds={}):
        self.type = type
        self.content = content
        self.host = host
        self.service = service
        # kwds are used by:
        #  *  pymon.messaging.listener.Listener's dispatch methods when
        #     connecting to remote network resources (providing needed client
        #     data); and
        #  *  MessageFactory for creating properly populated payloads (e.g.,
        #     email headers and content)
        self.kwds = kwds

class Message(RawMessage, pb.Copyable):
    '''
    For messages to be eligible for transport through callRemote, we inherit
    from pb.Copyable.

    This is what needs to be sent to the Listener.

    This class needs to be registered in the pymon.messaging.listener module.
    '''

class ReceiverMessage(pb.RemoteCopy, RawMessage):
    '''
    To allow in-coming messages to act as local representatives for remote
    messages, we inherit from pb.RemoteCopy.

    This is what the Listener creates when it receives a Message instance.

    This class needs to be registered in the pymon.messaging.listener module.
    '''

class MessageFactory(object):
    '''
    Though instantiated in workflow.rules, the factory ultimately gets its
    values when createMessages() is called in the plugin client code. It is the
    responsibility of each monitor client to pass kwd values to
    createMessages() that are needed when 1) creating the factory, and more
    importantly, 2) the Listener's appropriate dispatch method creates the
    actual messages that will be sent to the remote host.
    '''
    def __init__(self, type, **kwds):
        msg = Message(type=type, host=kwds['host'])
        # get service
        # create message body/content
        # get message-specific values
        if type == 'smtp':
            # set subject kwd
            # set to kwd
        elif type == 'rss':
            # set title, date, and link kwds
        elif type == 'irc':
            # set irc host and port kwds
            # set irc nick kwd
            # set irc channels (list) kwd
        elif type == 'snmp':
            pass
        elif type == 'im':
            pass
        elif type == 'mud':
            pass
        elif type == 'twitter':
            pass
        self.msg = msg


