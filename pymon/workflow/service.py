'''
pymon Workflow

For each service that is being monitored, it's own workflow
should exist, one that shares no session data with any other service,
as each service is completely independent.
'''
from pymon import utils
from pymon.config import cfg

from base import Workflow, WorkflowAware

states = cfg.state_definitions
# Create a workflow for managing states
stateWorkflow = Workflow()
for state, stateName in cfg.stateLookup.items():
    description = 'pymon is in %s state' % stateName.upper()
    stateWorkflow.addState(state, description=description, fullName=stateName)
# Setup workflow transitions -- the parameter passed to addTrans are:
#  * Transition name
#  * Legal source states
#  * Destination state
#  * Description
stateWorkflow.addTrans('Warning',
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.warn,
    description='pymon has gone from OK to WARN')
stateWorkflow.addTrans('Erring',
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.error,
    description='pymon has gone to state ERROR')
stateWorkflow.addTrans('Failing',
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.failed,
    description='pymon has gone to state FAILED')
stateWorkflow.addTrans('Recovering',
    [states.warn, states.error, states.unknown, states.failed],
    states.ok,
    description='pymon has resumed normal operation, but the previous '+ \
        'state was either WARN or ERROR')
stateWorkflow.addTrans('Escalating',
    [states.warn, states.error, states.escallated],
    states.escallated,
    description='pymon has received too many counts of a certain kind')
stateWorkflow.setInitState(states.unknown)

# define a workflow-aware for mangaging state
class ServiceState(WorkflowAware):
    '''
    '''
    def __init__(self, workflow):
        self.enterWorkflow(workflow)

    def onEnterNormal(self):
        print '+ Entering normal state...'

    def onLeaveNormal(self):
        print '- Leaving normal state...'

    def onEnterWarn(self):
        print '+ Entering warning state...'

    def onLeaveWarn(self):
        print '- Leaving warning state...'

    def onEnterError(self):
        print '+ Entering error state...'

    def onLeaveError(self):
        print '- Leaving error state...'

    def onEnterRecover(self):
        print '+ Entering recover state...'

    def onLeaveRecover(self):
        print '- Leaving recover state...'

    def onTransRecovering(self):
        print '* Transitioning in recovering state...'

    def onTransEscalating(self):
        print '* Issue unaddressed: escalating...'

# this is what should get imported by the pymon application:
serviceState = ServiceState(stateWorkflow)
