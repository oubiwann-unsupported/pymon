from twisted.python import components

class IDefaults(components.Interface):
    ""
    def getServiceName(self):
        ""
    def getMessageTemplate(self):
        ""
    def getOkThreshold(self):
        ""
    def getWarnThreshold(self):
        ""
    def getErrorThreshold(self):
        ""

class IPingDefaults(IDefaults):
    ""
    def getPingCount(self):
        ""
    def getPingBinary(self):
        ""
    def getCommand(self):
        ""

class IHttpDefaults(IDefaults):
    pass

class IEscalationGroup(components.Interface):
    ""
    def getGroupLevel(self):
        ""
    def getEmailAddresses(self):
        ""

class IEscalationGroups(components.Interface):
    ""
    def getState(self):
        "checck to see if enabled or disabled"
    def getGroups(self):
        "return an iterator of EscalationGroup instances"
    
class IHost(components.Interface):
    ""
    def getHostName(self):
        ""
    def getEscalationGroups(self):
        ""

class IService(components.Interface):
    ""
    def getDefaults(self):
        ""
    def getHosts(self):
        ""
    def getServiceType(self):
        ""

class IConfig(components.Interface):
    '''
    The programming interface for a pymon
    configuration.
    '''
    def getAllServices(self):
        '''
        Get an interator of all services.
        '''
    def getService(self):
        '''
        Get a particular service. Unique services are determined by
        hostname + domain name + service type.
        '''
    def getSystem(self):
        '''
        Get the system configuration.
        '''
