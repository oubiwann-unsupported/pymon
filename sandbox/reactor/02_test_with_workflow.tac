from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol
from adytum.workflow.base import Workflow, WorkflowAware
from random import random

####################
# database section #
####################
class StateDataRow(object):
    def __init__(self, id):
        self.id = id
        self.last_data = None
        self.last_state = None
    def setLastData(self, data):
        self.last_data = data
    def setLastState(self, state):
        self.last_state = state
    def getLastData(self):
        return self.last_data
    def getLastState(self):
        return self.last_state

####################
# workflow section #
####################
state_wf = Workflow()
state_wf.addState('Normal', description='pymon is in normal operation with no alerts')
state_wf.addState('Warn', description='pymon is in WARN state')
state_wf.setInitState('Normal')

state_wf.addTrans('Warning', 'Normal', 'Warn',
    description='pymon has gone from OK to WARN')
state_wf.addTrans('Recovering', 'Warn', 'Normal',
    description='pymon has resumed normal operation')

class ServiceState(WorkflowAware):
    def __init__(self, workflow=state_wf):
        self.enterWorkflow(workflow, None, "Just Created")
    def onEnterNormal(self):
        print 'workflow: + Entering normal state...'
    def onLeaveNormal(self):
        print 'workflow: - Leaving normal state...'
    def onEnterWarn(self):
        print 'workflow: + Entering warning state...'
    def onLeaveWarn(self):
        print 'workflow: - Leaving warning state...'
    def onTransRecovering(self):
        print 'workflow: * Transitioning in recovering state...'

####################
# protocol section #
####################
class Process(ProcessProtocol):
    def __init__(self):
        self.data = ''
        self.pid = None
    def connectionMade(self):
        self.pid = self.transport.pid
        print "protocol: opened processes %s..." % self.pid
        self.transport.closeStdin()
    def outReceived(self, data):
        print "protocol: received data from process %d (%d bytes)" % \
            (self.pid, len(data))
        self.data = self.data + data
    def processEnded(self, status_object):
        print "protocol: process %d complete (status %d)" % \
            (self.pid, status_object.value.exitCode)
        print "protocol: %s" % self.data
    def errReceived(self, data): pass
    def outConnectionLost(self): pass
    def errConnectionLost(self): pass

##################
# client section #
##################
class TextEchoClient(Process):
    def __init__(self, name=None):
        self.name = name
        self.history = StateDataRow(id=name)
        self.workflow = ServiceState()
        Process.__init__(self)
    def parseData(self):
        (tag, data) = self.data.split(':')
        if tag == 'data':
            return data.strip()
    def processEnded(self, status_object):
        parsed_data = self.parseData()
        print "client: name = %s" % self.name
        print "client: data row id = %s" % self.history.id
        print "client: last data = %s" % self.history.getLastData()
        print "client: parsed data = %s" % parsed_data
        print "client (workflow): last state = %s" % self.workflow.getLastStatename()
        print "client (workflow): this state = %s" % self.workflow.getStatename()
        try:
            self.workflow.doTrans('Warn')
        except: pass
        try:
            self.workflow.doTrans('Recovering')
        except: pass
        self.history.setLastData(parsed_data)

####################
# monitors section #
####################
def getProcessMonitors(count):
    processes = []
    random_data = ['data: yes', 'data: no', 'data: maybe']
    for i in range(0, count):
        command = '/bin/echo'
        params = random_data[int(random()*10) % 3]
        binary = 'echo'
        process = TextEchoClient(name='echo %s' % i)
        options = [command, params]
        processes.append((process, binary, options))
    return processes

INTERVAL = 20

################
# main section #
################
def runMonitors():
  [ reactor.spawnProcess(*x) for x in getProcessMonitors(4) ]

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)
server = internet.TimerService(INTERVAL, runMonitors)
server.setServiceParent(pymonServices)
