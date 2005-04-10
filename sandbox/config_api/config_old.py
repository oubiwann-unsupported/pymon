from constants import *
import interfaces

storage = {
    'dbdir'             : DBDIR,
    'fsdir'             : FSDIR,
}

configuration = {
    'installdir'        : INSTALL_DIR,
    'galleriesdir'      : GALLERY_DIR,
    'port'              : PORT,
    'storage'           : storage,
    'appname'           : APP_NAME,
}

class Config(object):
    def __init__(self, config):
        for key, val in config.items():
            if type(val).__name__ == 'dict':
                subobj = Config(val)
                setattr(self, key, subobj)
            else:
                setattr(self, key, val)

cfg = Config(configuration)

class IniConfig:
    __implements__ = (IIniConfig, )

class XmlConfig:
    __implements__ = (IXmlConfig, )
