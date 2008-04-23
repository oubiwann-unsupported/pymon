# Copyright (C) 2002-2004 Juan David Ibanez Palomar <jdavid@itaapy.com>
#               2002 Thilo Ernst <Thilo.Ernst@dlr.de>
#               2005 Duncan McGreggor <duncan@adytum.us>
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

class WorkflowStateError(WorkflowError):
    pass

class WorkflowTransitionError(WorkflowError):
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

class StatesCollection(dict):
    """
    A customized dict to keep track of workflow states.

    >>> states = StatesCollection()
    >>> states
    {}
    >>> states['state 1'] = object()
    >>> states['state 2'] = object()
    >>> states['state 3'] = object()
    >>> keys = states.keys()
    >>> keys.sort()
    >>> keys
    ['state 1', 'state 2', 'state 3']
    >>> states['state 1'] != None
    True
    >>> states.get('state 1') != None
    True
    >>> states.get('state 4') != None
    False
    >>> states['state 4']
    Traceback (most recent call last):
    WorkflowStateError: Unknown state name 'state 4'
    """
    def __getitem__(self, stateName):
        item = self.get(stateName)
        if not item:
            raise WorkflowStateError, "Unknown state name '%s'" % stateName
        return item

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
    >>> wf.addTrans('SimpleOkay', 'Normal', 'Normal',
    ...   description='The app has gone to OK')

    >>> t = wf.states['Normal'].transitions['SimpleOkay']
    >>> t.name
    'SimpleOkay'
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
    WorkflowTransitionError: Can't transition for unregistered state (to): 'Escalate'

    >>> wf.addTrans('Recovering', ['Warn', 'Error'], 'Normal',
    ...   description='The app has resumed normal operation')
    Traceback (most recent call last):
    WorkflowTransitionError: Can't transition for unregistered state (from): 'Warn'

    >>> wf.addTrans('Recovering', 'Error', 'Normal',
    ...   description='The app has resumed normal operation')

    >>> t = wf.states['Error'].transitions['Recovering']
    >>> t.name
    'Recovering'
    >>> t.stateFrom
    'Error'
    >>> t.stateTo
    'Normal'

    # can we register it again?
    >>> wf.addTrans('Recovering', 'Error', 'Normal',
    ...   description='The app has resumed normal operation')
    Traceback (most recent call last):
    WorkflowTransitionError: Transition 'Recovering' has already been registered

    # test the transition registry and related methods
    >>> index = wf.getTransIndex(wf.states['Normal'], 'Erring', wf.states['Error'])
    >>> index
    'Normal|Erring|Error'
    >>> trans = wf.getTransByIndex(index)
    >>> trans.stateFrom
    'Normal'
    >>> trans.name
    'Erring'
    >>> trans.stateTo
    'Error'
    >>> trans = wf.getTransByObjects(wf.states['Error'], 'Okay', wf.states['Normal'])
    >>> trans.stateFrom
    'Error'
    >>> trans.name
    'Okay'
    >>> trans.stateTo
    'Normal'
    >>> trans = wf.getTransByObjects(wf.states['Error'], 'Bogus', wf.states['Normal'])
    Traceback (most recent call last):
    WorkflowTransitionError: Unknown transition name 'Bogus'
    >>> trans = wf.getTransByObjects(wf.states['Doh'], 'Bogus', wf.states['Normal'])
    Traceback (most recent call last):
    WorkflowStateError: Unknown state name 'Doh'

    # try setting up a bogus initial state
    >>> wf.setInitState('Recovering')
    Traceback (most recent call last):
    WorkflowError: invalid initial state: 'Recovering'

    # setup initial state
    >>> wf.setInitState('Normal')
    >>> wf.initialState.name
    'Normal'

    """
    def __init__(self, initialState=None):
        """
        Initialize the workflow.
        """
        self.states = StatesCollection()
        self.transitionRegistry = {}
        self.setInitState(initialState)

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
        if not self.states:
            self.initialState = None
        elif name not in self.states:
            raise WorkflowError, "invalid initial state: '%s'" % name
        else:
            self.initialState = self.states[name]

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
                except WorkflowStateError:
                    msg = "Can't transition for unregistered state (from): '%s'"
                    raise WorkflowTransitionError, msg % sf
                try:
                    st = self.states[st]
                except WorkflowStateError:
                    msg = "Can't transition for unregistered state (to): '%s'"
                    raise WorkflowTransitionError, msg % st
                sf.addTrans(transition)
                index = self.getTransIndex(sf, name, st)
                result = self.transitionRegistry.setdefault(index, transition)
                if result != transition:
                    msg = "Transition '%s' has already been registered"
                    raise WorkflowTransitionError, msg % transition.name

    def getTransByIndex(self, index):
        try:
            return self.transitionRegistry[index]
        except KeyError, e:
            sf, name, st = str(e).split('|')
            raise WorkflowTransitionError, "Unknown transition name '%s'" % name

    def getTransIndex(self, stateFrom, name, stateTo=''):
        stateToName = ''
        if stateTo:
            stateToName = stateTo.name
        return "%s|%s|%s" % (stateFrom.name, name, stateToName)

    def getTransByObjects(self, stateFrom, name, stateTo):
        index = self.getTransIndex(stateFrom, name, stateTo)
        return self.getTransByIndex(index)

    def getTransByStateAndName(self, stateFrom, name):
        indexPart = self.getTransIndex(stateFrom, name, '')
        return [y for x,y in self.transitionRegistry.items()
                if x.startswith(indexPart)][0]

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

    # define the actions for a workflow-aware class
    >>> class StatusChecker(WorkflowAware):
    ...   def __init__(self, workflow=None):
    ...     WorkflowAware.__init__(self)
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
    ...   def onTransRecovering(self):
    ...     print '* Transitioning in recovering state...'
    ...   def onTransEscalating(self):
    ...     print '* Issue unaddressed: escalating...'
    ...   def getStateName(self, id): return id
    ...   def getStateID(self, name): return name
    ...   def onLeave(self):
    ...     print '-- Leaving...'
    ...   def onTrans(self):
    ...     print '** Transitioning...'
    ...   def onEnter(self):
    ...     print '++ Entering...'

    # constants
    >>> OK = 'Normal'
    >>> WARN = 'Warn'
    >>> ERROR = 'Error'

    # lookup
    >>> def getTestStateName(index):
    ...   if index == -1: return None
    ...   if index == 0: return OK
    ...   if index == 1: return WARN
    ...   if index == 2: return ERROR

    # put the workflow though its paces
    >>> def processStates(test_pattern):
    ...   statusChecker = StatusChecker(workflow=wf)
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
    ...       statusChecker.doTrans('Recovering')
    ...     elif state is not OK and count > 2 and state != 'Escalate':
    ...       statusChecker.doTrans('Escalating')
    ...     elif state is WARN:
    ...       statusChecker.doTrans('Warning')
    ...     elif state is ERROR:
    ...       statusChecker.doTrans('Erring')

    >>> test_pattern = [0,1,2]
    >>> processStates(test_pattern)
    + Entering normal state...
    -- Leaving...
    - Leaving normal state...
    ** Transitioning...
    ++ Entering...
    + Entering warning state...
    -- Leaving...
    - Leaving warning state...
    ** Transitioning...
    ++ Entering...
    + Entering error state...

    >>> test_pattern = [0,2,0,0]
    >>> processStates(test_pattern)
    + Entering normal state...
    -- Leaving...
    - Leaving normal state...
    ** Transitioning...
    ++ Entering...
    + Entering error state...
    -- Leaving...
    - Leaving error state...
    ** Transitioning...
    * Transitioning in recovering state...
    ++ Entering...
    + Entering normal state...

    >>> test_pattern = [2,2,2,2,2]
    >>> processStates(test_pattern)
    + Entering normal state...
    -- Leaving...
    - Leaving normal state...
    ** Transitioning...
    ++ Entering...
    + Entering error state...
    -- Leaving...
    - Leaving error state...
    ** Transitioning...
    ++ Entering...
    + Entering error state...
    -- Leaving...
    - Leaving error state...
    ** Transitioning...
    ++ Entering...
    + Entering error state...
    -- Leaving...
    - Leaving error state...
    ** Transitioning...
    * Issue unaddressed: escalating...
    ++ Entering...
    -- Leaving...
    ** Transitioning...
    * Issue unaddressed: escalating...
    ++ Entering...
    """
    def __init__(self):
        self.workflow = None
        self.thisWorkflowState = None
        self.lastWorkflowState = None

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

        if not self.workflow.states.has_key(initialState.name):
            raise WorkflowError, "invalid initial state: '%s'" % initialState

        self.setState(initialState)
        self.thisWorkflowState = initialState
        self.lastWorkflowState = None

        # Call app-specific enter-state handler for initial state, if any
        name = self.thisWorkflowState.name.title()
        self.dispatch('Enter', name)(*args, **kwds)

    def setState(self, state):
        self.lastWorkflowState = self.thisWorkflowState
        self.thisWorkflowState = state

    def getStateName(self, stateID):
        """
        Subclasses must define this method.
        """
        raise Exception, NotImplemented

    def getStateID(self, stateName):
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
        # Get the current state
        trans = self.workflow.getTransByStateAndName(self.thisWorkflowState,
                                                     transname)
        nextState = self.workflow.states[trans.stateTo]
        # if defined, call 'onLeave' for every leave-state
        self.dispatch('Leave')(*args, **kwds)
        # call app-specific leave-state  handler if any
        name = self.thisWorkflowState.name.title()
        self.dispatch('Leave', name)(*args, **kwds)

        # Set the new state - before this is called, the current state is the
        # state prior to the transition; after this is called, that becomes the
        # last state and the destination state becomes the current state.
        self.setState(nextState)

        # if defined, call 'onTrans' for every transition-state
        self.dispatch('Trans')(*args, **kwds)
        # call app-specific transition handlers in order
        self.dispatch('Trans', transname.title())(*args, **kwds)

        # if defined, call 'onEnter' for every transition-state
        self.dispatch('Enter')(*args, **kwds)
        # call app-specific enter-state handler if any
        name = self.thisWorkflowState.name.title()
        self.dispatch('Enter', name)(*args, **kwds)

    def noOp(self, *args, **kwds):
        return

    def dispatch(self, type, name=''):
        """
        Return the method for the given type and name.
        """
        name = 'on%s%s' % (type, name)
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return self.noOp

    def currentStatus(self):
        return self.thisWorkflowState.name
    currentStatus = property(currentStatus)

    def previousStatus(self):
        return self.thisWorkflowState.name
    previousStatus = property(previousStatus)

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
