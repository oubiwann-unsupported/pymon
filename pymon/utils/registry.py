class Error(Exception):
    pass


class RegistrationError(Error):
    pass


class Registry(dict):
    '''
    # create a registry and add values
    >>> reg = Registry()
    >>> data1 = {'apples':'oranges'}
    >>> data2 = "No comparison!"
    >>> data3 = ['oranges', 'are', 'better']
    >>> reg.add('mydict', data1)

    # check for adding the same name again
    >>> reg.add('mydict', data2)
    Traceback (most recent call last):
    RegistrationError: An object with that name is already registered.

    # add some more and do a lookup
    >>> reg.add('astring', data2)
    >>> reg.add('alist', data3)
    >>> reg.lookup('astring')
    'No comparison!'

    # look for something that's not there
    >>> reg.lookup('doesntexist')

    # get everything that's registered
    >>> items = reg.getRegisteredObjects()
    >>> items.sort()
    >>> print items
    [('alist', ['oranges', 'are', 'better']), ('astring', 'No comparison!'), ('mydict', {'apples': 'oranges'})]

    # let's add another string to show the returned lists
    >>> reg.add('stringTwo', 'Another string?!')
    >>> reg.getRegisteredObjectsOfType('str')
    ['No comparison!', 'Another string?!']
    >>> reg.getRegisteredObjectsOfType('list')
    [['oranges', 'are', 'better']]
    >>> reg.getRegisteredObjectsOfType('dict')
    [{'apples': 'oranges'}]

    # test with old-style classes
    >>> class Config:
    ...   def __init__(self):
    ...     self.name = 'Alice'
    >>> cfg = Config()
    >>> reg.add('config', cfg)
    >>> reg.getRegisteredObjectsOfType('instance')[0].name
    'Alice'
    >>> reg.getFirstRegisteredObjectOfType('instance').name
    'Alice'

    # get rid of it now
    >>> reg.unregisterObject('config')
    >>> reg.unregisterObject('config')
    Traceback (most recent call last):
    RegistrationError: 'config' is not in the registry.

    # make sure it's really not there
    >>> reg.getRegisteredObjectsOfType('instance')

    # let's remove some more stuff
    >>> reg.unregisterObject('mydict')
    >>> reg.unregisterObject('alist')

    # test with new-style classes
    >>> class Config(object):
    ...   def __init__(self):
    ...     self.name = 'Bob'
    >>> cfg = Config()
    >>> reg.add('config', cfg)
    >>> reg.getRegisteredObjectsOfType('Config')[0].name
    'Bob'
    >>> items = reg.getRegisteredObjects()
    >>> items.sort()
    >>> print [ x[0] for x in items ]
    ['astring', 'config', 'stringTwo']
    '''
    def lookup(self, aName):
        return self.get(aName)

    getRegisteredObject = lookup

    def getRegisteredObjects(self):
        return [ x for x in self.items() if x[0] != '_types_reg' ]

    def getRegisteredObjectsOfType(self, aType):
        objs = self['_types_reg'].get(aType)
        if objs: return objs

    def getFirstRegisteredObjectOfType(self, aType):
        return self.getRegisteredObjectsOfType(aType)[0]

    def unregisterObject(self, aName):
        this_object = self.lookup(aName)
        this_type = type(this_object).__name__
        try:
            self['_types_reg'][this_type].remove(this_object)
            self['_types_reg'].pop(this_type)
            self.pop(aName)
        except KeyError:
            raise RegistrationError, "'%s' is not in the registry." % aName

    def getattr(self, aAttr):
        return self.__getattribute__(aAttr)

    def setattr(self, aName, aValue):
        self.__setattr__(aName, aValue)

    def _registerObjectType(self, aObject):
        this_type = type(aObject).__name__
        self.setdefault('_types_reg', {})
        self['_types_reg'].setdefault(this_type, [])
        self['_types_reg'][this_type].append(aObject)

    def add(self, aName, aObject):
        if not self.lookup(aName):
            self._registerObjectType(aObject)
            self.update({aName:aObject})
            self.setattr(aName, aObject)
        else:
            raise RegistrationError, \
                "An object with that name is already registered."


def _test():
    import doctest, registry
    doctest.testmod(registry)

if __name__ == '__main__':
    _test()
