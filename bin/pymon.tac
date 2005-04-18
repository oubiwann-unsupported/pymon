from twisted.internet import reactor
from twisted.internet import task

from adytum.app.pymon.api import config
from adytum.app.pymon.api import utilities

from plugins import monitors

INTERVAL = 20
#INTERVAL = 1
Service = utilities.getService(config.pymoncfg.system.database.type)

def runMonitors():

    # fire each ping monitor configuration off on the reactor
    #[ reactor.spawnProcess(*x) for x in monitors.getPingMonitors() ]

    # fire each process monitor configureation off on the reactor

    # fire each page monitor configureation off on the reactor

    # fire each HTTP return status configuration off on the reactor
    [ reactor.connectTCP(*x) for x in monitors.getHTTPMonitors() ]

sched = task.LoopingCall(runMonitors)
sched.start(INTERVAL)
reactor.run()
