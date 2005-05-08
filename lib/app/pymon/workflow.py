'''
pymon Workflow

For any given workflow instance, in pymon, we will want it to be a
Singleton. The state of the system will be stored in base.State
which in turn is used in base.Workflow. The last thing we want is
multiple instances of workflow with different state information.
'''
from adytum.workflow.singleton import SingletonWorkflow \
    as Workflow
from adytum.workflow.singleton import SingletonWorkflowAware \
    as WorkflowAware

# Instantiate and setup workflow states
state_wf = base.Workflow()
state_wf.addState('Normal', description='pymon is in normal operation with no alerts')
state_wf.addState('Warn', description='pymon is in WARN state')
state_wf.addState('Error', description='pymon is in ERROR state')
state_wf.addState('Escalate', description='pymon is escalating')
state_wf.setInitState('Normal')

# Setup workflow transitions
state_wf.addTrans('Warning', ['Normal', 'Warn', 'Error'], 'Warn',
    description='pymon has gone from OK to WARN')
state_wf.addTrans('Erring', ['Normal', 'Warn', 'Error'], 'Error',
    description='pymon has gone to state ERROR')
state_wf.addTrans('Recovering', ['Warn', 'Error'], 'Recover',
    description='pymon has resumed normal operation, but the previous state was either WARN or ERROR')
state_wf.addTrans('Escalating', ['Warn', 'Error', 'Escalate'], 'Escalate',
    description='pymon has received too many counts of a certain kind')

# define a workflow-aware for mangaging state
class PyMonState(WorkflowAware):

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
pymon_state = PyMonState(workflow=state_wf)


