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
        self.kwds = kwds

class Message(RawMessage, pb.Copyable):
    '''
    For messages to be eligible for transport through callRemote, we inherit
    from pb.Copyable.
    '''

class ReceiverMessage(pb.RemoteCopy, RawMessage):
    '''
    To allow in-coming messages to act as local representatives for remote
    messages, we inherit from pb.RemoteCopy.
    '''
