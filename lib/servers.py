from twisted.application import internet

from nevow import vhost
from nevow import appserver

from pymon import utils
from pymon.ui.web import pages

import agents

from registry import globalRegistry

def addWebServer(rootService):
    factories = globalRegistry.factories
    vResource = vhost.VHostMonsterResource()
    webroot = pages.Root(factories)
    webroot.putChild(globalRegistry.config.web.vhost_root, vResource)
    site = appserver.NevowSite(webroot)
    port = globalRegistry.config.web.port
    webserver = internet.TCPServer(port, site)
    webserver.setServiceParent(rootService)

def addConfigServer(rootService):
    interval = globalRegistry.config.admin.config_update.interval
    config_check = internet.TimerService(interval, 
        utils.refreshConfig)
    config_check.setServiceParent(rootService)

def addBackupServer(rootService):
    interval = globalRegistry.config.admin.backups.interval
    backups = internet.TimerService(interval, 
        globalRegistry.state.backup)
    backups.setServiceParent(rootService)

def addProcessServer(rootService):
    factory = agents.ProcessServerFactory()
    port = globalRegistry.config.agents.port
    server = internet.TCPServer(port, factory)
    server.setServiceParent(rootService)

