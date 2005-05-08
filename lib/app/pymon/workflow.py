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
pywf = base.Workflow()
pywf.addState('Normal', description='App is in normal operation with no alerts')
pywf.addState('Warn', description='App is in WARN state')
pywf.addState('Error', description='App is in ERROR state')
pywf.addState('Escalate', description='App is escalating')
pywf.setInitState('Normal')

# Setup workflow transitions
pywf.addTrans('Warning', ['Normal', 'Warn', 'Error'], 'Warn',
    description='The app has gone from OK to WARN')
pywf.addTrans('Erring', ['Normal', 'Warn', 'Error'], 'Error',
    description='The app has gone to state ERROR')
pywf.addTrans('Recovering', ['Warn', 'Error'], 'Recover',
    description='The app has resumed normal operation, but the previous state was either WARN or ERROR')
pywf.addTrans('Escalating', ['Warn', 'Error', 'Escalate'], 'Escalate',
    description='The app has received too many counts of a certain kind')


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
pymon_state = PyMonState(workflow=pywf)


