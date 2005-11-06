from twisted.application import internet

from nevow import appserver

from pymon.ui.web import pages

import agents

from registry import globalRegistry

def addWebServer(rootService):
    factories = globalRegistry.factories
    webroot = appserver.NevowSite(pages.Root(factories))
    port = globalRegistry.config.system.web.port
    webserver = internet.TCPServer(int(port), webroot)
    webserver.setServiceParent(rootService)

def addBackupServer(rootService):
    interval = globalRegistry.config.system.backups.state_data.interval
    backups = internet.TimerService(int(interval), globalRegistry.state.backup)
    backups.setServiceParent(rootService)

def addProcessServer(rootService):
    factory = agents.ProcessServerFactory()
    port = globalRegistry.config.system.agents.port
    server = internet.TCPServer(int(port), factory)
    server.setServiceParent(rootService)

