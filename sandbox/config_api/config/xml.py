import cElementTree as ElementTree
from zope.interface import implements
from interfaces.config import *

'''
>>> import cElementTree as et
>>> tree = et.parse('simple.xml')
>>> root = tree.getroot()
>>> root.findall('services/service')

def processChildren(elements):
    for element in elements:
        print element.tag
        if element.tag == 'service':
            print 'Service type: %s' % element.attrib['type']
        try:
            processChildren(element.getchildren())
        except:
            pass
        # what to do if it's a service
        # what to do if it's a system setting
        # what to do if it's a constant

'''

class PingDefaults(object):

    implements(IPingDefaults)

class Service(object):

    implements(IService)

    def __init__(self, service):
        self.service = service

    def getDefaults(self):
        return 

    def getHosts(self):
        pass

    def getServiceType(self):
        pass

class XmlConfig(object):

    implements(IConfig)

    def __init__(self, filename):
        self.filename = filename
        tree = ElementTree.parse(self.filename)
        self.root = tree.getroot()

    def getServices(self):
        return self.root.getiterator('service')

    def getService(self, service_type):
        for service in self.root.findall('services/service'):
            if service.get('type') == service_type:
                yield Service(service)

    def getSystem(self):
        return self.root.find('system')

class IniConfig(object):
    pass
