import re

test_string = '''
###
# Top-level config sections
###
config.enabled: Services that are globally enabled
config.disabled: Services that are globally diabled
config.services: Service configurations
config.system: Configuration settings for the pymon system in general
config.constants: pymon constants
config.globalNames: various names that are used at a high level

###
# Set the type of pymon configuration this is. pymon can be configured
# to scan and process configuration by either services or groups of
# services.
#
# Valid options: services, groups
# Default: services
###
config.enabled.groupsOrServices: services

###
# The service types that are enabled.
#
# Valid options: ping, http status, http text, ftp status, smtp status, smtp send, dns dig
# Default:
###
config.enabled.serviceTypes: ping, http status

###
# The service types that are disabled
###
config.diaabled.groupsOrServices: services
config.disabled.serviceTypes: http text, local process, dns dig

###
# pymon system
###
config.system.uid: pymon
config.system.gid: pymon
config.system.installPrefix: /usr/local
config.system.backups.stateData.interval: 300
config.system.backups.stateData.directory: data
config.system.backups.stateData.filename: backup.pkl
config.system.mail.fromAddress: pymon@adytum.us
config.system.mail.sendmail: /usr/sbin/sendmail
config.system.agents.port: 10999

###
# pymon constants
###
config.constants.states.unknown: -1
config.constants.states.ok: 1
config.constants.states.recovering: 2
config.constants.states.warn: 3
config.constants.states.error: 4
config.constants.states.failed: 5
'''
class Value(dict):
    '''
    # with no passed parameters
    >>> v = Value('super')
    >>> v.value
    'super'
    >>> v.type
    >>> v.default
    >>> v.valid
    []
    >>> v['value']
    'super'
    >>> v['type']
    >>> v['default']
    >>> v['valid']
    []

    # now with keywords
    >>> v = Value('False', type='Boolean', default='True', valid=['True', 'False'])
    >>> v.value
    'False'
    >>> v['value']
    'False'
    >>> v.type
    'Boolean'
    >>> v['valid']
    ['True', 'False']
    >>> v.valid
    ['True', 'False']

    # test dict stuff
    >>> o = v.keys()
    >>> o.sort()
    >>> o
    ['data', 'default', 'type', 'valid', 'value']
    >>> o = v.values()
    >>> o.sort()
    >>> o
    [None, ['True', 'False'], 'Boolean', 'False', 'True']
    
    '''
    def __init__(self, val, **kw):
        struct = {
            'value'     : val,
            'type'      : kw.get('type'),
            'data'      : kw.get('data'),
            'default'   : kw.get('default'),
            'valid'     : kw.get('valid') or [],
        }
        self.update(struct)

    value = property(
        lambda s: s['value'], lambda s,v: s.update({'value': v})
    )
    data = property(
        lambda s: s['data'], lambda s,v: s.update({'data': v})
    )
    type = property(
        lambda s: s['type'], lambda s,v: s.update({'type': v})
    )
    default = property(
        lambda s: s['default'], lambda s,v: s.update({'default': v})
    )
    valid = property(
        lambda s: s['valid'], lambda s,v: s.update({'valid': v})
    )

    def __repr__(self):
        mod = self.__module__
        name = self.__class__.__name__
        return "<%s.%s '%s', %s>" % (mod, name, self.value, self.data)

class ConfigDictOld(dict):
    def __init__(self, items, final=None):
        # 'items' is the list of sub-names that 
        # comprise the dotten config key
        while items:
            item = items.pop(0)
            data = ConfigDict(items, final)
            print (item, final, data)
            if data:
                valueobj = Value(final, data=data)
            else:
                valueobj = Value(final)
            self.setdefault(item, valueobj)
            setattr(self, item, valueobj)

class ConfigDict(dict):
    def __init__(self, items, final, dct={}):
        # 'items' is the list of sub-names that 
        # comprise the dotten config key
        self.update(dct)
        while items:
            item = items.pop()
            data = ConfigDict(items, final)
            print (item, final, data)
            if data:
                valueobj = Value(final, data=data)
            else:
                valueobj = Value(final)
            self.setdefault(item, valueobj)
            setattr(self, item, valueobj)

class ConfigString(object):
    '''
    >>> config = ConfigString(test_string)
    '''
    def __init__(self, a_string):
        '''
        # first build a test string
        >>> s = """
        ... testing
        ... one, two, three
        ... 
        ... # a comment
        ...    
        ... testing."""

        # now make sure it does the right thing
        # on initialization
        >>> s = ConfigString(s)
        >>> s.lines
        ['testing', 'one, two, three', 'testing.']
        '''
        lines = a_string.split('\n')
        self.lines = [ line.strip() for line in lines 
            if line.strip() and not line.startswith('#') ]

        self._dict = {}

    def _processLines(self):
        '''
        # first build a test string
        >>> s = """
        ... a: test 1
        ... a.b: test 2
        ... a.b.c: test 3
        ... a.b.c.d: test 4
        ... """

        # now lets see if our dict gets set
        # properly
        >>> s = ConfigString(s)
        >>> s._processLines()
        >>> #s._dict.a
        >>> #s._dict.a.value
        >>> #s._dict.a.data
        '''
        for line in self.lines:
            # Configuration entries are key/value pairs, and 
            # can  be delimited by either a ':' or a '='
            key, val = re.split('[:=]', line, 1)
            key = key.strip()
            val = val.strip()
            # The configuration keys are representative of
            # python objects, and therefore use dotted names
            names = key.split('.')
            print "call dict stuff..."
            self._dict = ConfigDict(names, val, dct=self._dict)
            #self._dict = self._recurse(names, val)

    def _recurse(self, items, final):
        while items:
            item = items.pop(0)
            data = self._recurse(items, final)
            print (item, final, data)
            if data:
                valueobj = Value(final, data=data)
            else:
                valueobj = Value(final)
            #self._dict.setdefault(item, valueobj)
            #setattr(self._dict, item, valueobj)

    def _guessType(self, val):
        pass

def _test():
    import doctest, s2
    doctest.testmod(s2)

if __name__ == '__main__':
    _test() 
