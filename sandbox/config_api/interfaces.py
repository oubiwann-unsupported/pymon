from twisted.python import components

class IConfig(components.Interface):
    pass

class IIniConfig(components.Interface):
    pass

class IXmlConfig(components.Interface):
    pass
