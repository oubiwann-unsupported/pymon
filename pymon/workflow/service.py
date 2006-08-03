'''
pymon Workflow

For each service that is being monitored, it's own workflow
should exist, one that shares no session data with any other service,
as each service is completely independent.
'''
from base import WorkflowAware

# Setup workflow transitions -- the parameter passed to addTrans are:
#  * Transition name
#  * Legal source states
#  * Destination state
#  * Description
states = cfg.state_definitions
stateWorkflow.addTrans('Warning', 
    [states.ok, states.warn, states.error], 
    'Warn',
    description='pymon has gone from OK to WARN')
stateWorkflow.addTrans('Erring', 
    ['Normal', 'Warn', 'Error'], 
    'Error',
    description='pymon has gone to state ERROR')
stateWorkflow.addTrans('Recovering', 
    ['Warn', 'Error'], 
    'Normal',
    description='pymon has resumed normal operation, but the previous '+ \ 
        'state was either WARN or ERROR')
stateWorkflow.addTrans('Escalating', 
    ['Warn', 'Error', 'Escalate'], 
    'Escalate',
    description='pymon has received too many counts of a certain kind')

# define a workflow-aware for mangaging state
class ServiceState(WorkflowAware):
    '''
    '''
    def __init__(self, workflow=None):
        self.enterWorkflow(workflow, None, "Just Created")

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
serviceState = ServiceState(workflow=stateWorkflow)


