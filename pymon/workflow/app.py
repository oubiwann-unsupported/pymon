'''
pymon Workflow

For any given workflow instance, in pymon, we will want it to be a
Singleton. The state of the system will be stored in base.State
which in turn is used in base.Workflow. The last thing we want is
multiple instances of workflow with different state information.
'''
from base import Workflow, WorkflowAware


# Instantiate and setup workflow states
appWf = Workflow()
appWf.addState(
    'Normal', 
    description='pymon is in normal operation with no alerts')
appWf.setInitState('Normal')

# Setup workflow transitions


# define a workflow-aware for mangaging state
class AppState(WorkflowAware):
    '''
    '''
    def __init__(self, workflow=None):
        self.enterWorkflow(workflow, None, "Just Created")


# this is what should get imported by the pymon application:
appState = AppState(workflow=appWf)


