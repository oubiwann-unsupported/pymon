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
class WorkflowError(Exception):
    pass

class WorkflowState(object):
    """
    This class is used to describe a state. A state has transitions
    to other states.

    >>> state = WorkflowState('Normal',
    ...   description='Normal operation with no alerts')
    >>> state.name
    'Normal'
    >>> state['description']
    'Normal operation with no alerts'

    >>> class Trans(object): pass
    >>> trans1 = Trans()
    >>> trans1.name = 'Test Transition 1'
    >>> trans2 = Trans()
    >>> trans2.name = 'Test Transition 2'
    >>> state.addTrans(trans1)
    >>> state.addTrans(trans2)
    >>> transNames = state.transitions.keys()
    >>> transNames.sort()
    >>> transNames
    ['Test Transition 1', 'Test Transition 2']
    >>> transObjs = state.transitions.values()
    >>> [x != None for x in transObjs]
    [True, True]

    """
    def __init__(self, name, **kwds):
        """
        Initialize the state.
        """
        self.name = name
        self.metadata = kwds
        self.transitions = {}

    def __getitem__(self, key):
        """
        Access to the metadata as a mapping.
        """
        return self.metadata.get(key)

    def addTrans(self, transition):
        """
        Adds a new transition.
        """
        self.transitions[transition.name] = transition

class Transition(object):
    """
    This class is used to describe transitions. Transitions come from
    one state and go to another.

    >>> stateFrom = WorkflowState('Normal',
    ...   description='Normal operation with no alerts')
    >>> stateTo = WorkflowState('Error',
    ...   description='App is in ERROR state')
    >>> trans = Transition('Erring', stateFrom, stateTo,
    ...   description='The app has gone to state ERROR')
    >>> trans.name
    'Erring'
    >>> trans.stateFrom.name
    'Normal'
    >>> trans.stateTo.name
    'Error'
    >>> trans['description']
    'The app has gone to state ERROR'

    """
    def __init__(self, name, stateFrom, stateTo, **kwds):
        """
        Initialize the transition.
        """
        self.name = name
        self.stateFrom = stateFrom
        self.stateTo = stateTo
        self.metadata = kwds

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

    >>> wf = Workflow()
    >>> wf.addState('Normal',
    ...   description='Normal operation with no alerts')
    >>> wf.addState('Error',
    ...   description='App is in ERROR state')
    >>> states = wf.states.keys()
    >>> states.sort()
    >>> states
    ['Error', 'Normal']

    # a simple workflow transitions
    >>> wf.addTrans('Okay', 'Normal', 'Normal',
    ...   description='The app has gone to OK')

    >>> t = wf.states['Normal'].transitions['Okay']
    >>> t.name
    'Okay'
    >>> t.stateFrom
    'Normal'
    >>> t.stateTo
    'Normal'

    # setup workflow transitions
    >>> wf.addTrans('Okay', ['Normal', 'Error'], 'Normal',
    ...   description='The app has gone to OK')

    >>> t = wf.states['Normal'].transitions['Okay']
    >>> t.name
    'Okay'
    >>> t.stateFrom
    'Normal'
    >>> t.stateTo
    'Normal'

    >>> t = wf.states['Error'].transitions['Okay']
    >>> t.name
    'Okay'
    >>> t.stateFrom
    'Error'
    >>> t.stateTo
    'Normal'

    # another transition
    >>> wf.addTrans('Erring', ['Normal', 'Error'], 'Error',
    ...   description='The app has gone to state ERROR')

    >>> t = wf.states['Normal'].transitions['Erring']
    >>> t.name
    'Erring'
    >>> t.stateFrom
    'Normal'
    >>> t.stateTo
    'Error'

    >>> t = wf.states['Error'].transitions['Erring']
    >>> t.name
    'Erring'
    >>> t.stateFrom
    'Error'
    >>> t.stateTo
    'Error'

    >>> wf.addTrans('Escalating', 'Error', 'Escalate',
    ...   description='The app has gone too long without acknowledgement')
    Traceback (most recent call last):
    WorkflowError: unregistered state (to): 'Escalate'

    >>> wf.addTrans('Recovering', ['Warn', 'Error'], 'Normal',
    ...   description='The app has resumed normal operation')
    Traceback (most recent call last):
    WorkflowError: unregistered state (from): 'Warn'

    >>> wf.addTrans('Recovering', 'Error', 'Normal',
    ...   description='The app has resumed normal operation')

    >>> t = wf.states['Error'].transitions['Recovering']
    >>> t.name
    'Recovering'
    >>> t.stateFrom
    'Error'
    >>> t.stateTo
    'Normal'

    # setup initial state
    >>> wf.setInitState('Recovering')
    Traceback (most recent call last):
    WorkflowError: invalid initial state: 'Recovering'

    >>> wf.setInitState('Normal')
    >>> wf.initialState
    'Normal'

    """
    def __init__(self, initialState=None):
        """
        Initialize the workflow.
        """
        self.states = {}
        self.initialState = initialState

    def addState(self, name, **kwds):
        """
        Adds a new state.

        The keywords argument lets one add arbitrary metadata to
        describe the transition.
        """
        self.states[name] = WorkflowState(name, **kwds)

    def setInitState(self, name):
        """
        Sets the default initial state.
        """
        if name not in self.states:
            raise WorkflowError, "invalid initial state: '%s'" % name
        self.initialState = name

    def addTrans(self, name, stateFrom, stateTo, **kwds):
        """
        Adds a new transition, 'stateFrom' and 'stateTo' are
        respectively the origin and destination states of the
        transition.

        The keywords argument lets one add arbitrary metadata to
        describe the transition.
        """
        if not isinstance(stateFrom, list):
            stateFrom = [stateFrom]
        if not isinstance(stateTo, list):
            stateTo = [stateTo]
        for sf in stateFrom:
            for st in stateTo:
                transition = Transition(name, sf, st, **kwds)
                try:
                    sf = self.states[sf]
                except KeyError:
                    raise WorkflowError, "unregistered state (from): '%s'" % sf
                try:
                    st = self.states[st]
                except KeyError:
                    raise WorkflowError, "unregistered state (to): '%s'" % st
                sf.addTrans(transition)

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
    >>> wf.addTrans('Okay', ['Normal', 'Escalate', 'Warn', 'Error'], 'Normal',
    ...   description='The app has gone to OK')
    >>> wf.addTrans('Warning', ['Normal', 'Warn', 'Error'], 'Warn',
    ...   description='The app has gone to state WARN')
    >>> wf.addTrans('Erring', ['Normal', 'Warn', 'Error'], 'Error',
    ...   description='The app has gone to state ERROR')
    >>> wf.addTrans('Recovering', ['Warn', 'Error', 'Escalate'], 'Normal',
    ...   description='The app has resumed normal operation')
    >>> wf.addTrans('Escalating', ['Warn', 'Error', 'Escalate'], 'Escalate',
    ...   description='The issues has not been addressed')

    # setup initial state
    >>> wf.setInitState('Normal')

    # define a workflow-aware class
    >>> class AppState(WorkflowAware):
    ...   def __init__(self, workflow=None):
    ...     self.enterWorkflow(workflow, None)
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
    ...   def setState(self, number):
    ...     try:
    ...       self.lastWorkflowState = self.thisWorkflowState
    ...       self.lastWorkflowStateName = self.thisWorkflowStateName
    ...     except AttributeError:
    ...       self.lastWorkflowState = 'Normal'
    ...       self.lastWorkflowStateName = 'Normal'
    ...     self.lastWorkflowState = number
    ...     self.lastWorkflowStateName = number
    ...   def getStateName(self, id): return id

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

    def enterWorkflow(self, workflow=None, initialState=None, *args, **kwds):
        """
        [Re-]Bind this object to a specific workflow, if the 'workflow'
        parameter is omitted then the object associated workflow is kept.
        This lets us, for example, specify the associated workflow with a
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
        self.thisWorkflowState = initialState
        self.thisWorkflowStateName = self.getStateName(initialState)
        self.lastWorkflowState = None

        # Call app-specific enter-state handler for initial state, if any
        self.dispatch('Enter', self.thisWorkflowStateName.title())(*args, **kwds)

    def setState(self, stateID):
        """
        Subclasses must define this method.
        """
        # XXX this shouldn't depend on application-level configuration or other
        # definitions. One option is to provide the ability to pass a lookup
        # function or to set one as an object attribute. Another option is to
        # raise a NotImplemented error, requiring subclasses to write it as
        # needed, complete with configuration code, if that's what they need.
        raise Exception, NotImplemented

    def getStateName(self, stateID):
        """
        Subclasses must define this method.
        """
        raise Exception, NotImplemented

    def doTrans(self, transname, *args, **kwds):
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
            # XXX this is the source of the bug, since the current state may
            # not have the same "legal" transitions as the last state. In other
            # words, this kind of lookup by array index is just wrong
            self.lastWorkflowState = state.transitions[transname].stateFrom
            state = state.transitions[transname].stateTo
            stateName = self.getStateName(state)
        except KeyError, e:
            tmpl = "transition '%s' is invalid from state '%s (%s)'"
            msg = tmpl % (transname, self.thisWorkflowState, e)
            #import pdb;pdb.set_trace()
            raise WorkflowError, msg

        # call app-specific leave-state  handler if any
        self.dispatch('Leave', self.thisWorkflowStateName.title())(*args, **kwds)

        # Set the new state
        self.setState(state)

        # call app-specific transition handlers in order
        self.dispatch('Trans', transname.title())(*args, **kwds)

        # call app-specific enter-state handler if any
        self.dispatch('Enter', stateName.title())(*args, **kwds)

    def noOp(self, *args, **kwds):
        return

    def dispatch(self, type, name):
        """
        Return the method for the given type and name.
        """
        name = 'on%s%s' % (type, name)
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return self.noOp

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
