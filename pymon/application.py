import re
import os
from Queue import Queue
try:
    import cPickle as pickle
except ImportError:
    import pickle

from zope.interface import implements

from twisted.persisted import sob
from twisted.persisted.sob import Persistent

from pymon import exceptions
from pymon import utils
from pymon.config import cfg
from pymon.interfaces import IState
from pymon.utils.logger import log
from pymon.utils.registry import Registry
from pymon.workflow.base import Workflow
from pymon.workflow.service import ServiceState, stateWorkflow


initialCheckData = {
    'org': '',
    'node': '',
    'service type': '',
    'service': '',
    'count': 0,
    'count ok': 0,
    'count warn': 0,
    'count error': 0,
    'count failed': 0,
    'count unknown': 0,
    'count maintenance': 0,
    'count disabled': 0,
    'current status': -1,
    'previous status': -1,
    'current status name': '',
    'previous status name': '',
    'desc': '',
    'data': '',
    'last check': '',
    'last ok': '',
    'last warn': '',
    'last error': '',
    'last failed': '',
    }


class InitialCheckData(dict):
    '''
    The data structure for the data that monitors will set.
    '''
    def __init__(self):
        self.update(initialCheckData)


class BaseState(Persistent):
    '''
    # create a state and add some test data
    >>> s = BaseState()
    >>> s.data = {'test data': 'Here it is!'}
    >>> print s.data
    {'test data': 'Here it is!'}

    # try to restore it
    >>> s.restore()
    Traceback (most recent call last):
    exceptions.StateRestoreError: It appears that state was never saved; cannot restore

    # try to save without a filename
    >>> s.save()
    Traceback (most recent call last):
    exceptions.StateSaveError: You have not yet saved this instance and so must provide a filename.

    # save it
    >>> saveFile = 'tmppckl_pkl'
    >>> s.save(saveFile)

    # change the state data and print it
    >>> s.data = {'test data': 'this is going away... soon...'}
    >>> print s.data
    {'test data': 'this is going away... soon...'}

    # restore old state data and make sure that the last changes
    # made to the state are now overwritten with the original
    # state data
    >>> t = BaseState()
    >>> t.setFilename(saveFile)
    >>> t.restore()
    >>> print t.data
    {'test data': 'Here it is!'}

    # lets update the data, save it, and make sure it restores
    >>> t.data.update({'new data': 'doh!'})
    >>> t.data['new data']
    'doh!'
    >>> t.save()
    >>> t.data = {}
    >>> t.restore()
    >>> t.data['new data']
    'doh!'
    >>> t.data['test data']
    'Here it is!'

    # lets cleanup that file
    #>>> os.unlink(s.filename)
    #>>> os.path.exists(s.filename)
    #False
    '''
    def __init__(self, data={}):
        Persistent.__init__(self, self, '')
        self.data = data
        self.filename = None

    def __getstate__(self):
        return self.__dict__

    def set(self, key, value):
        self.data[key] = value
        self.__dict__[key] = value

    def get(self, key):
        return self.data[key]

    def setFilename(self, filename):
        self.filename = filename

    def getFilename(self):
        return self.filename

    def save(self, filename=None):
        if not filename:
            filename = self.filename
        else:
            self.filename = filename
        #p = Persistent.save(self, filename=filename)
        #fh = open(filename, 'w+')
        #import pdb;pdb.set_trace()
        #pickle.dump(self, fh)
        #fh.close()

    def restore(self):
        if not self.filename:
            raise exceptions.StateRestoreError, \
                "It appears that state was never saved; cannot restore"
        if os.path.exists(self.filename):
            s = sob.load(self.filename, 'pickle')
            for key, val in s.__dict__.items():
                setattr(self, key, val)

    def items(self):
        return self.data.items()


class MonitorState(BaseState):
    '''
    This is a state machine and adapter. It adapts a monitor instance to a
    state object. The state for a given monitor is retrieved by callint the
    interface:
        state = IState(monitorInstance)
    The associated monitor is accessed via the monitor attribute:
        cfg = state.monitor.cfg

    Monitors need to have their own state data files, named according to
    a convention. MonitorState provides a method to do this:

    >>> m = MonitorState('http status://adytum.us')
    >>> m.data.get('current status')
    -1
    >>> m.data.get('org')
    ''
    >>> m.save()
    >>> m.restore()
    >>> m.data.get('current status')
    -1
    >>> m.set('current status', 3)
    >>> m.data.get('current status')
    3
    >>> m.save()
    >>> m.restore()
    >>> m.data.get('current status')
    3
    '''
    implements(IState)

    def __init__(self, monitor):
        self.monitor = monitor
        BaseState.__init__(self, data=InitialCheckData())
        self.setFilename()
        self.workflow = ServiceState(stateWorkflow)

    def setFilename(self, filename=None):
        backupDir = self.monitor.cfg.app.admin.backups.state_dir
        if not filename:
            filename = self.monitor.uid
        self.filename = os.path.join(backupDir,
            re.sub('[^0-9A-Za-z_]', '_', filename))
        self.data.filename = self.filename
        log.debug("Backup file named '%s'." % self.filename)

def setNonChangingState(state, stateNum, uid):
    stateName = cfg.getStateNameFromNumber(stateNum)
    type = utils.getFriendlyTypeFromURI(uid)
    host = utils.getHostFromURI(uid)
    org = cfg.getCheckConfigFromURI(uid).org
    state.set('current status', stateNum)
    state.set('current status name', stateName)
    state.set('count '+stateName, 1)
    state.set('node', host)
    state.set('service', type)
    if org:
        state.set('org', org)
    return state


class History(Queue, object):
    '''
    >>> h = History(3)
    >>> h.add('test 1')
    >>> h.queue
    deque(['test 1'])
    >>> h.add('test 2')
    >>> h.queue
    deque(['test 1', 'test 2'])
    >>> h.add('test 3')
    >>> h.queue
    deque(['test 1', 'test 2', 'test 3'])
    >>> h.last
    Traceback (most recent call last):
    AttributeError: 'History' object has no attribute 'last'

    >>> h.add('test 4')
    >>> h.queue
    deque(['test 2', 'test 3', 'test 4'])
    >>> h.last
    'test 1'
    >>> h.add('test 5')
    >>> h.getLastRemoved()
    'test 2'
    '''
    def setattr(self, aName, aValue):
        self.__setattr__(aName, aValue)

    def getattr(self, aName):
        return self.__getattribute__(aName)

    def setLastRemoved(self, aItem):
        self.setattr('last', aItem)

    def getLastRemoved(self):
        return self.getattr('last')

    def add(self, aItem):
        try:
            self.put_nowait(aItem)
        except:
            self.removeItem()
            self.add(aItem)

    def removeItem(self):
        self.setLastRemoved(self.get())


# setup global registry
globalRegistry = Registry()
state       = BaseState()
history     = History()
factories   = {}

app_state = os.path.join(cfg.admin.backups.state_dir,
    cfg.admin.backups.application_state)
state.setFilename(app_state)


# load previous app state data, if available
try:
    state.restore()
    log.info("Restoring previous application state...")
except IOError:
    state.save()

globalRegistry.add('state', state)
globalRegistry.add('history', history)
globalRegistry.add('factories', factories)


def _test():
    import doctest, application
    doctest.testmod(application)

if __name__ == '__main__':
    _test()
