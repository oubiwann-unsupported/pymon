# Copyright (C) 2002-2004 Juan David Ibanez Palomar <jdavid@itaapy.com>
#               2002 Thilo Ernst <Thilo.Ernst@dlr.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
# Modified  by Duncan McGreggor starting 2005.
"""
The workflow module simplifies the task of writing workflow systems.

The development of a workflow system can be split in three steps:

 1. Define the workflow as a graph with the 'Workflow' class:
    1.1 Create an instance of the 'Workflow' class;
    1.2 Add to this instance the different states and optionally
        set the initial state;
    1.3 Add the transitions that let to go from one state to another.
 2. Define the objects that will follow the workflow:
    2.1 inherite from the 'WorkflowAware' class;
    2.2 introduce each object into the workflow with the 'enter_workflow'
        method.
 3. Associate the application semantics to the workflow aware objects
    by implementing the 'onenter', 'onleave' and 'ontrans' methods.
    Examples of "application semantics" are:
    - change the security settings of an object so it becomes public or
      private;
    - send an email to a user or a mailing list;
"""
from pymon.config import cfg

states = cfg.state_definitions

class WorkflowError(Exception):
    pass

class WorkflowState(object):
    """
    This class is used to describe a state. A state has transitions
    to other states.
    """
    def __init__(self, **kw):
        """
        Initialize the state.
        """
        self.transitions = {}
        self.metadata = kw

    def __getitem__(self, key):
        """
        Access to the metadata as a mapping.
        """
        return self.metadata.get(key)

    def addTrans(self, name, transition):
        """
        Adds a new transition.
        """
        self.transitions[name] = transition

class Transition(object):
    """
    This class is used to describe transitions. Transitions come from
    one state and go to another.
    """
    def __init__(self, stateFrom, stateTo, **kw):
        """
        Initialize the transition.
        """
        self.stateFrom = stateFrom
        self.stateTo = stateTo
        self.metadata = kw

    def __getitem__(self, key):
        """
        Access to the metadata as a mapping.
        """
        return self.metadata.get(key)

class Workflow(object):
    """
    This class is used to describe a workflow (actually it's just a
    graph). A workflow has states (one of them is the initial state),
    and states have transitions that go to another state.
    """
    def __init__(self, initialState=None):
        """
        Initialize the workflow.
        """
        self.states = {}
        self.initialState = initialState

    def addState(self, name, **kw):
        """
        Adds a new state.

        The keywords argument lets to add arbitrary metadata to
        describe the transition.
        """
        self.states[name] = WorkflowState(**kw)

    def setInitState(self, name):
        """
        Sets the default initial state.
        """
        if name not in self.states:
            raise WorkflowError, "invalid initial state: '%s'" % name
        self.initialState = name

    def addTrans(self, name, stateFrom, stateTo, **kw):
        """
        Adds a new transition, 'stateFrom' and 'stateTo' are
        respectively the origin and destination states of the
        transition.

        The keywords argument lets to add arbitrary metadata to
        describe the transition.
        """
        if not isinstance(stateFrom, list):
            stateFrom = [stateFrom]
        if not isinstance(stateTo, list):
            stateTo = [stateTo]
        for sf in stateFrom:
            for st in stateTo:
                transition = Transition(sf, st, **kw)
                try:
                    sf = self.states[sf]
                except KeyError:
                    raise WorkflowError, "unregistered state (from): '%s'" % sf
                try:
                    st = self.states[st]
                except KeyError:
                    raise WorkflowError, "unregistered state (to): '%s'" % st
                sf.addTrans(name, transition)

class WorkflowAware(object):
    """
    Mixin class to be used for workflow aware objects. The instances of
    a class that inherits from WorkflowAware can be "within" the workflow,
    this means that they keep track of the current state of the object.

    Specific application semantics for states and transitions can be
    implemented as methods of the WorkflowAware-derived "developer 
    class". These methods get associated with the individual
    states and transitions by a simple naming scheme. For example, 
    if a workflow has two states 'Private' and 'Public', and a 
    transition 'Publish' that goes from 'Private' to 'Public', 
    the following happens when the transition is executed:

      1. if implemented, the method 'onLeavePrivate' is called
         (it is called each time the object leaves the 'Private' state)
      2. if implemented, the method 'onTransPublish' is called
         (it is called whenever this transition is executed)
      3. if implemented, the method 'onEnterPublic' is called
         (it is called each time the object enters the 'Public' state)

    These state/transition "handlers" can also be passed arguments
    from the caller of the transition; for instance, in a web-based
    system it might be useful to have the HTTP request that triggered 
    the current transition available in the handlers.

    A simple stack with three methods, 'pushdata', 'popdata' adn 'getdata',
    is implemented. It can be used, for example, to keep record of the states
    the object has been in.

    # Lets test this puppy in action. 
    # Instantiate and setup workflow states:
    >>> wf = Workflow()
    >>> wf.addState('Normal',
    ...   description='Normal operation with no alerts')
    >>> wf.addState('Warn',
    ...   description='App is in WARN state')
    >>> wf.addState('Error',
    ...   description='App is in ERROR state')
    >>> wf.addState('Escalate',
    ...   description='App is escalating')
    
    # setup workflow transitions
    >>> wf.addTrans('Normaling', ['Normal', 'Escalate', 'Warn', 'Error'], 'Normal',
    ...   description='The app has gone to OK')
    >>> wf.addTrans('Warning', ['Normal', 'Warn', 'Error'], 'Warn',
    ...   description='The app has gone from OK to WARN')
    >>> wf.addTrans('Erring', ['Normal', 'Warn', 'Error'], 'Error',
    ...   description='The app has gone to state ERROR')
    >>> wf.addTrans('Recovering', ['Warn', 'Error', 'Escalate'], 'Normal',
    ...   description='The app has resumed normal operation, but the previous state was either WARN or ERROR')
    >>> wf.addTrans('Escalating', ['Warn', 'Error', 'Escalate'], 'Escalate',
    ...   description='The app has received too many counts of a certain kind')

    # setup initial state
    >>> wf.setInitState('Normal')

    # define a workflow-aware class
    >>> class AppState(WorkflowAware):
    ...   def __init__(self, workflow=None):
    ...     self.enterWorkflow(workflow, None, "Just Created")
    ...   def onEnterNormal(self):
    ...     print '+ Entering normal state...'
    ...   def onLeaveNormal(self):
    ...     print '- Leaving normal state...'
    ...   def onEnterWarn(self):
    ...     print '+ Entering warning state...'
    ...   def onLeaveWarn(self):
    ...     print '- Leaving warning state...'
    ...   def onEnterError(self):
    ...     print '+ Entering error state...'
    ...   def onLeaveError(self):
    ...     print '- Leaving error state...'
    ...   def onEnterRecover(self):
    ...     print '+ Entering recover state...'
    ...   def onLeaveRecover(self):
    ...     print '- Leaving recover state...'
    ...   def onTransRecovering(self):
    ...     print '* Transitioning in recovering state...'
    ...   def onTransEscalating(self):
    ...     print '* Issue unaddressed: escalating...'

    # constants
    >>> OK = 'Normal'
    >>> WARN = 'Warn'
    >>> ERROR = 'Error'
    >>> RECOV = 'Recover'

    # lookup
    >>> def getTestStateName(index):
    ...   if index == -1: return None
    ...   if index == 0: return OK
    ...   if index == 1: return WARN
    ...   if index == 2: return ERROR

    # put the workflow though its paces
    >>> def processStates(test_pattern):
    ...   app_state = AppState(workflow=wf)
    ...   count = 0
    ...   for i in range(0, len(test_pattern)):
    ...     state = getTestStateName(test_pattern[i])
    ...     if i == 0: last_state = -1
    ...     else: last_state = test_pattern[i-1]
    ...     #print last_state
    ...     last_state = getTestStateName(last_state)
    ...     if state == last_state:
    ...       count += 1
    ...     else:
    ...       count = 0
    ...     #print 'count: %s' % count
    ...     #print 'state: %s' % state
    ...     #print 'last state: %s' % last_state
    ...
    ...     if state is OK and last_state not in [OK, None]:
    ...       app_state.doTrans('Recovering')
    ...     elif state is not OK and count > 2 and state != 'Escalate':
    ...       app_state.doTrans('Escalating')
    ...     elif state is WARN:
    ...       app_state.doTrans('Warning')
    ...     elif state is ERROR:
    ...       app_state.doTrans('Erring')

    >>> test_pattern = [0,1,2]
    >>> processStates(test_pattern)
    - Leaving normal state...
    + Entering warning state...
    - Leaving warning state...
    + Entering error state...

    >>> test_pattern = [0,2,0,0]
    >>> processStates(test_pattern)
    - Leaving normal state...
    + Entering error state...
    - Leaving error state...
    * Transitioning in recovering state...
    + Entering normal state...

    >>> test_pattern = [2,2,2,2,2]
    >>> processStates(test_pattern)
    - Leaving normal state...
    + Entering error state...
    - Leaving error state...
    + Entering error state...
    - Leaving error state...
    + Entering error state...
    - Leaving error state...
    * Issue unaddressed: escalating...
    * Issue unaddressed: escalating...
    """
    def __getstate__(self):
        return self.__dict__

    def enterWorkflow(self, workflow=None, initialState=None, *args, **kw):
        """
        [Re-]Bind this object to a specific workflow, if the 'workflow'
        parameter is omitted then the object associated workflow is kept.
        This lets, for example, to specify the associate workflow with a
        class varible instead of with an instance attribute.

        The 'initialState' parameter is the workflow state that should be
        taken on initially (if omitted or None, the workflow must provide
        a default initial state).

        Extra arguments args are passed to the enter-state handler (if any)
        of the initial state. 
        """
        # Set the associated workflow
        if workflow is not None:
            self.workflow = workflow

        # Set the initial state
        if initialState is None:
            initialState = self.workflow.initialState

        if not initialState:
            raise WorkflowError, 'undefined initial state'

        if not self.workflow.states.has_key(initialState):
            raise WorkflowError, "invalid initial state: '%s'" % initialState

        self.setState(initialState)
        self.thisWorkflowStateName = cfg.getStateNameFromNumber(initialState)
        self.lastWorkflowState = None

        # Call app-specific enter-state handler for initial state, if any
        name = 'onEnter%s' % self.thisWorkflowStateName.title()
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

    def setState(self, number):
        try:
            self.lastWorkflowState = self.thisWorkflowState
            self.lastWorkflowStateName = self.thisWorkflowStateName
        except AttributeError:
            self.lastWorkflowState = states.unknown
            self.lastWorkflowStateName = cfg.getStateNameFromNumber(states.unknown)
        self.thisWorkflowState = number
        self.thisWorkflowStateName = cfg.getStateNameFromNumber(number)

    def doTrans(self, transname, *args, **kw):
        """
        Performs a transition, changes the state of the object and
        runs any defined state/transition handlers. Extra 
        arguments are passed down to all handlers called.
        """
        # Get the workflow
        workflow = self.workflow

        # Get the current state
        state = self.workflow.states[self.thisWorkflowState]
        
        try:
            # Get the new state name
            self.lastWorkflowState = state.transitions[transname].stateFrom
            state = state.transitions[transname].stateTo
            stateName = cfg.getStateNameFromNumber(state)
        except KeyError:
            raise WorkflowError, \
                  "transition '%s' is invalid from state '%s'" \
                  % (transname, self.thisWorkflowState)
        
        # call app-specific leave- state  handler if any
        name = 'onLeave%s' % self.thisWorkflowStateName.title()
        print "Checking for '%s()' method..." % name
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

        # Set the new state
        self.setState(state)

        # call app-specific transition handler if any
        name = 'onTrans%s' % transname.title()
        print "Checking for '%s()' method..." % name
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

        # call app-specific enter-state handler if any
        name = 'onEnter%s' % stateName.title()
        print "Checking for '%s()' method..." % name
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

    def getStatename(self):
        """Return the name of the current state."""
        return self.thisWorkflowStateName

    def getLastStatename(self):
        return self.lastWorkflowStateName

    def getState(self):
        """Returns the current state instance."""
        state = self.thisWorkflowStateName
        return self.workflow.states.get(state)

    # Implements a stack that could be used to keep a record of the
    # object way through the workflow.
    # A tuple is used instead of a list so it will work nice with
    # the ZODB.
    workflowHistory = ()

    def pushdata(self, data):
        """
        Adds a new element to the top of the stack.
        """
        self.workflowHistory = self.workflowHistory + (data,)

    def popdata(self):
        """
        Removes and returns the top stack element.
        """
        if len(self.workflowHistory) == 0:
            return None
        data = self.workflowHistory[-1]
        self.workflowHistory = self.workflowHistory[:-1]
        return data

    def getdata(self):
        """
        Returns the data from the top element without removing it.
        """
        if len(self.workflowHistory) == 0:
            return None
        return self.workflowHistory[-1]


def _test():
    import doctest, base
    doctest.testmod(base)

if __name__ == '__main__':
    _test()
