from ConfigParser import ConfigParser
from constants import INSTALL_DIR, TYPE

class Configuration(object):
    '''
    >>> from config import pymon
    >>> p = pymon.pings
    >>> p.sort()
    >>> p
    ['i360.xnet.esecuresystems.com :: ping', 'shell1.adytum.us :: ping', 'shell2.adytum.us :: ping', 'www.divorce-md.com :: ping', 'www.esecuresystems.com :: ping']
    >>> pymon.setPingConfigs()
    >>> p = pymon.getPingConfigs()
    >>> p.sort()
    >>> p
    ['i360.xnet.esecuresystems.com :: ping', 'shell1.adytum.us :: ping', 'shell2.adytum.us :: ping', 'www.divorce-md.com :: ping', 'www.esecuresystems.com :: ping']
    >>> pymon.setHTTPConfigs()
    >>> h = pymon.getHTTPConfigs()
    >>> h.sort()
    >>> h
    ['accuratemachinery.com :: http', 'adytumsolutions.com :: http', 'bgrfamilylaw.com :: http', 'wmsoa.org :: http']

    '''

    def __init__(self, inifile):
        inidata = ConfigParser()
        inidata.read(inifile)
        self.inidata = inidata
        self.__pings = []
        self.__http = []
        self.__sections = {}
        self.setPingConfigs()
        self.setHTTPConfigs()
        self.setSections()

    def setSections(self):
        self.__sections = self.inidata.__dict__['_sections']

    def getSection(self, section, sub_section):
        key = '%s :: %s' % (section, sub_section)
        return self.__sections[key]

    def getStateDefs(self):
        return self.getSection('constants', 'states')

    def getSections(self):
        return self.__sections
        
    def getTypes(self, service_type):
        types = []
        for section in self.inidata.sections():
            if self.inidata.has_option(section, TYPE):
                if self.inidata.get(section, TYPE) == service_type:
                    types.append(section)
        return types

    def setPingConfigs(self):
        self.__pings = self.getTypes('ping')

    def getPingConfigs(self):
        return self.__pings

    def setHTTPConfigs(self):
        self.__http = self.getTypes('http')

    def getHTTPConfigs(self):
        return self.__http

    def setAllLocalProcessTypes(self):
        pass

    def setAllRemoteProcessTypes(self):
        pass

    def setAllSNMPTypes(self):
        pass

    def setAllSMTPTypes(self):
        pass

    def setAllDirectoryTypes(self):
        pass

    sections = property(getSections,
        "This property provides access to all the sections in dict form.")

    pings = property(getPingConfigs,
        "This property provides access to the list of sections that are of 'ping' type.")

    http = property(getHTTPConfigs,
        "This property provides access to all the sections that are of 'http' type.")


pymon = Configuration('%s/conf/pymon.ini' % INSTALL_DIR)

def _test():
    import doctest, config
    return doctest.testmod(config)

if __name__ == '__main__':
    _test()

