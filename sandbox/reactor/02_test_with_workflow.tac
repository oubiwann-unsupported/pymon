from twisted.application import service, internet
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ProcessProtocol
from adytum.workflow.base import Workflow, WorkflowAware
from random import random

####################
# workflow section #
####################
state_wf = Workflow()
state_wf.addState('Normal', description='pymon is in normal operation with no alerts')
state_wf.addState('Warn', description='pymon is in WARN state')
state_wf.setInitState('Normal')

state_wf.addTrans('Warning', ['Warn', 'Normal'], 'Warn',
    description='pymon has gone from OK to WARN')
state_wf.addTrans('Recovering', ['Warn', 'Normal'], 'Normal',
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
        print 'workflow: * Recovering...'

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
class TextEchoClient(Process, ClientState):
    def __init__(self, name=None):
        self.name = name
        self.history = None
        self.uid = ('pymon instance 1', 'host2.adytum.us', self.name)
        Process.__init__(self)
    def setHistory(self, state_data):
        self.state_data = state_data
        # the first time through, this will populate the value
        # corresponding to index self.uid with a fresh workflow 
        # instance; if the index exists, the one in state_data 
        # will be used
        self.workflow = self.state_data.setdefault(self.uid, ServiceState())
    def updateHistory(self, state):
        pass
    def parseData(self):
        (tag, data) = self.data.split(':')
        if tag == 'data':
            return data.strip()
    def processEnded(self, status_object):
        parsed_data = self.parseData()
        last_state = self.workflow.getStatename()
        print "client: name = %s" % self.name
        print "client (workflow): last state = %s" % last_state
        print "client: parsed data = %s" % parsed_data
        if parsed_data in ['no', 'maybe'] and last_state != 'Warn':
            self.workflow.doTrans('Warning')
        elif parsed_data == 'yes' and last_state != 'Normal':
            self.workflow.doTrans('Recovering')
        print "client (workflow): this state = %s" % self.workflow.getStatename()
        print ""
        self.state_data[self.uid] = self.workflow

####################
# monitors section #
####################
def getProcessMonitors(count, state_data):
    processes = []
    random_data = ['data: yes', 'data: no', 'data: maybe']
    for i in range(0, count):
        command = '/bin/echo'
        params = random_data[int(random()*10) % 3]
        binary = 'echo'
        process = TextEchoClient(name='echo %s' % i)
        process.setHistory(state_data)
        options = [command, params]
        processes.append((process, binary, options))
    return processes

INTERVAL = 10

################
# main section #
################
# each state will have its own unique id based on pymon instance
# name, monnitored host name, and service name
#
# state_data[(pymon_name, host_name, service_name)] = state
state_data = {}

def runMonitors():
    [ reactor.spawnProcess(*x) for x in getProcessMonitors(2, state_data) ]

def backupStateData():
    pass

application = service.Application("pymon")
pymonServices = service.IServiceCollection(application)

monitor = internet.TimerService(INTERVAL, runMonitors)
monitor.setServiceParent(pymonServices)
backup = internet.TimerService(INTERVAL, backupStateData)
backup.setServiceParent(pymonServices)
