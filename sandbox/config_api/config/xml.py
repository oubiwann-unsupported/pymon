import cElementTree as ElementTree
from twisted.python.components import implements
from interfaces.config import *

'''
>>> import cElementTree as et
>>> tree = et.parse('simple.xml')
>>> root = tree.getroot()
>>> root.findall('services/service')
'''

class PingDefaults(object):

    implements(IPingDefaults)
    

class Service(object):

    implements(IService)

    def getDefaults(self):
        pass

    def getHosts(self):
        pass

    def getServiceType(self):
        pass

class Config(object):

    implements(IConfig)

    def __init__(self, filename):
        self.filename = filename
        tree = ElementTree.parse(self.filename)
        self.root = tree.getroot()

    def getServices(self):
        return self.root.findall('services/service')

    def getService(self, service_type):
        return [ x for x in root.findall('services/service') if x.get('type') == service_type ]

    def getSystem(self):
        return self.root.find('system')
