from zope.interface import Interface, implements

from twisted.python.components import Componentized
from twisted.python.components import registerAdapter

class IURIGetter(Interface):
    '''
    A Utility for getting the URI.
    '''

class Mixin(object):

    def getURI(self, uid)
        print "dummy://%s" % uid


    def otherStuff(self):
        pass

class MyClient(object):
    def __init__(self):
        .setComponent(IURIGetter)


class MyClientFactory(object):
    pass

#################################################
class ISquare(Interface):
    pass

class IArea(Interface):
    pass

class IColor(Interface):
    pass


class Area(object):
    implements(IArea)
    sideLength = 0
    def getSideLength(self):
        return self.sideLength
    
    def setSideLength(self, sideLength):
        self.sideLength = sideLength

    def area(self):
        raise NotImplementedError, "Subclasses must implement area"

class Color(object):
    implements(IColor)
    def __init__(self, original):
        self.original = original

    def setColor(self, color):
      self.color = color
    
    def getColor(self):
      return self.color
    

class Square(object):
    implements(IShape)
    def adaptColor(self, color):
        self.color = color

class AdaptColor(object):
    color = None


s = Square()
s.adaptColor(AdaptColor
