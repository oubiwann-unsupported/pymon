from twisted.internet import reactor
from twisted.internet import task

from sqlobject.sqlite import builder

from adytum.app.pymon import monitors
from adytum.app.pymon.datamodel import Service

INTERVAL = 20
#INTERVAL = 1

def runMonitors():

    # fire each ping monitor configuration off on the reactor
    #[ reactor.spawnProcess(*x) for x in monitors.getPingMonitors() ]

    # fire each process monitor configureation off on the reactor

    # fire each page monitor configureation off on the reactor

    # fire each HTTP return status configuration off on the reactor
    [ reactor.connectTCP(x[0],int(x[1]),x[2]) for x in monitors.getHTTPMonitors() ]

sched = task.LoopingCall(runMonitors)
sched.start(INTERVAL)
reactor.run()
