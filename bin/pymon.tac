from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task

from nevow import appserver

from adytum.app.pymon import config
from adytum.app.pymon import utilities
from adytum.app.pymon.ui.web import pages

import sys
sys.path.append('.')
from plugins import monitors

INTERVAL = 20
#INTERVAL = 1

# XXX this isn't being used right now, and may not ever...
#Service = utilities.getService(config.pymoncfg.system.database.type)

def runMonitors():

    # fire each ping monitor configuration off on the reactor
    [ reactor.spawnProcess(*x) for x in monitors.getPingMonitors() ]

    # fire each process monitor configuration off on the reactor

    # fire each page monitor configuration off on the reactor

    # fire each HTTP return status configuration off on the reactor
    #[ reactor.connectTCP(*x) for x in monitors.getHTTPMonitors() ]

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)
server = internet.TimerService(INTERVAL, runMonitors)
server.setServiceParent(pymonServices)

webroot = appserver.NevowSite(pages.TestPage())
webserver = internet.TCPServer(8080, webroot)
webserver.setServiceParent(pymonServices)

