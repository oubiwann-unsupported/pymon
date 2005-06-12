class Error(Exception):
    pass

class RegistrationError(Error):
    pass

class Registry(dict):
    '''
    >>> reg = Registry()
    >>> data1 = {'apples':'oranges'}
    >>> data2 = "No comparison!"
    >>> data3 = ['oranges', 'are', 'better']
    >>> reg.add('mydict', data1)
    >>> reg.add('mydict', data2)
    Traceback (most recent call last):
    RegistrationError: An object with that name is already registered.

    >>> reg.add('astring', data2)
    >>> reg.add('alist', data3)
    >>> reg.lookup('astring')
    'No comparison!'

    >>> reg.lookup('doesntexist')
    >>> items = reg.getRegisteredObjects()
    >>> items.sort()
    >>> print items
    [('alist', ['oranges', 'are', 'better']), ('astring', 'No comparison!'), ('mydict', {'apples': 'oranges'})]
    '''
    def lookup(self, aName):
        return self.get(aName)

    def getRegisteredObjects(self):
        return self.items()

    def getattr(self, aAttr):
        return self.__getattribute__(aAttr)

    def setattr(self, aName, aValue):
        self.__setattr__(aName, aValue)

    def add(self, aName, aObject):
        if not self.lookup(aName):
            self.update({aName:aObject})
            self.setattr(aName, aObject)
        else:
            raise RegistrationError, \
                "An object with that name is already registered."

globalRegistry = Registry()

def _test():
    import doctest, registry
    doctest.testmod(registry)

if __name__ == '__main__':
    _test()
