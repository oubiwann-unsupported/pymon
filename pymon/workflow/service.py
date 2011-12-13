'''
pymon Workflow

For each service that is being monitored, it's own workflow
should exist, one that shares no session data with any other service,
as each service is completely independent.
'''
from pymon.config import cfg

from base import Workflow, WorkflowAware


states = cfg.state_definitions
# Create a workflow for managing states
stateWorkflow = Workflow()


for state, stateName in cfg.stateLookup.items():
    description = 'pymon is in %s state' % stateName.upper()
    stateWorkflow.addState(state, description=description, fullName=stateName)


# Set up workflow transitions
transitionNames = {
    states.ok: 'Recovering',
    states.recovering: 'Recovering',
    states.warn: 'Warning',
    states.error: 'Erring',
    states.failed: 'Failing',
    states.acknowledged: 'Acknowledging',
    states.maintenance: 'Maintenance',
    states.disabled: 'Disabling',
    states.escalated: 'Escalating',
    states.unknown: 'Unknown',
}


# The parameter passed to addTrans are:
#  * Transition name
#  * Legal source states
#  * Destination state
#  * Description
stateWorkflow.addTrans(transitionNames[states.ok],
    [states.warn, states.error, states.unknown, states.failed],
    states.ok,
    description='pymon has resumed normal operation')


stateWorkflow.addTrans(transitionNames[states.warn],
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.warn,
    description='pymon has gone from OK to WARN')


stateWorkflow.addTrans(transitionNames[states.error],
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.error,
    description='pymon has gone to state ERROR')


stateWorkflow.addTrans(transitionNames[states.failed],
    [states.ok, states.warn, states.error, states.unknown, states.failed],
    states.failed,
    description='pymon has gone to state FAILED')


stateWorkflow.addTrans(transitionNames[states.escalated],
    [states.warn, states.error, states.escalated],
    states.escalated,
    description='pymon has received too many counts of a certain kind')


stateWorkflow.setInitState(states.unknown)

# define a workflow-aware for mangaging state
class ServiceState(WorkflowAware):
    '''
    '''
    def __init__(self, workflow=stateWorkflow):
        WorkflowAware.__init__(self)
        self.enterWorkflow(workflow)
        self.legal = cfg.getStateNames()

    def __getattr__(self, attr):
        error = None
        try:
            self.__getattribute__(attr)
        except AttributeError, e:
            error = e
        if attr in self.__getattribute__('legal'):
            class Func(object):
                def __init__(self, klass, attr):
                    self.attr = attr
                    self.klass = klass
                def __repr__(self):
                    return "<bound method %s.%s of %s>" % (
                        self.klass.__class__.__name__, attr, self.klass)
                def __call__(self):
                    if 'Leave' in self.attr:
                        verb = '- Leaving'
                        split = 'Leave'
                    elif 'Enter' in self.attr:
                        verb = '+ Entering'
                        split = 'Enter'
                    msg = "%s % state ..." % (verb, self.attr.split(split))
                    print msg
            return Func(self, attr)
        raise AttributeError

    def getStateName(self, stateID):
        return cfg.getStateNameFromNumber(stateID)

    def getStateID(self, stateName):
        return getattr(stateName.lower(), states)

    def onTrans(self, status='', rules=''):
        if rules.messaging.isSend(status):
            for msg in rules.messaging.messages:
                # XXX instantiate a pymon listener client and send the listener
                # the messages
                print " >>> Preparing to send message of type '%s' ..." % type

    def onTransRecovering(self):
        print '* Transitioning in recovering state...'

    def onTransEscalating(self):
        print '* Issue unaddressed: escalating...'

    def checkTransition(self, status, factory, rules=None):
        """

        """
        self.doTrans(transitionNames[status], status=status, rules=rules)


# this is what should get imported by the pymon application:
#serviceState = ServiceState(stateWorkflow)
