from zope.interface import Interface

class IConfigurable(Interface):
    '''
    Defines the API for things that wish to configure pymon.
    '''
    pass

class IStorable(Interface):
    '''
    Defines the API for things that wieh to store pymon data.
    '''
    pass

class IFormatable(Interface):
    '''
    Defines anything in pymon that is formattable.
    '''
    pass

class IMessage(IFormatable):
    '''
    Defines the API for Messages in pymon.
    '''
    pass
