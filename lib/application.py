import re
from Queue import Queue
try:
    import cPickle as pickle
except:
    import pickle

from twisted.python import log

class Error(Exception):
    pass

class StateBackupError(Error):
    pass

class State(dict):
    '''
    # create a state and add some test data
    >>> s = State(use_globalRegistry=False)
    >>> data = {'bogus data': 'nothin'}
    >>> s.update(data)
    >>> print s
    {'bogus data': 'nothin'}

    # now, try to back it up without a filename set
    >>> s.backup()
    Traceback (most recent call last):
    StateBackupError: The backup filename has not been set.

    # check restore too
    >>> s.restore()
    Traceback (most recent call last):
    StateBackupError: The backup filename has not been set.

    # okay, let's use the globalRegistry now
    >>> s = State()
    >>> data = {'test data': 'Here it is!'}
    >>> s.update(data)

    # since we don't have a top-level configuration object configured
    # to pull filename info from, we will set it ourselves.
    >>> s.setBackupFilename('/tmp/testbackup.pkl')
    >>> s.backup()
    >>> import os
    >>> os.path.exists(s.backup_file)
    True
    
    # change the state data and print it
    >>> more_data = {'test data': 'this is going away... soon...'}
    >>> s.update(more_data)
    >>> print s
    {'test data': 'this is going away... soon...'}

    # restore old state data and make sure that the last changes
    # made to the state are now overwritten with the original
    # state data
    >>> s.restore()
    >>> print s
    {'test data': 'Here it is!'}

    # lets cleanup that file
    >>> os.unlink(s.backup_file)
    >>> os.path.exists(s.backup_file)
    False
    '''
    def __init__(self, uid=None, use_globalRegistry=True):
        import os
        if not use_globalRegistry:
            self.setBackupFilename(None)
        else:
            from registry import globalRegistry
            cfg = globalRegistry.config
            if uid:
                # Specific backup
                filename = os.path.join(cfg.backups.state_dir,
                    re.sub('[^0-9A-Za-z_]', '_', uid))
            else:
                # General backup
                filename = 'app.pkl'
            self.backup_file = os.path.join(cfg.prefix, 
                cfg.backups.base_dir, filename)
            if os.path.exists(self.backup_file):
                self.restore()
                os.unlink(self.backup_file)
            # Initialize data strcuture for state - we're using 
            # setdefault here, so this doesn't need to be in an 'else'
            # block. The addeded benefit is that if something is missing
            # from any of the pickled data structures, they get a 
            # default value set.
            #
            # XXX this is going to move into configuration. At that time,
            # a list of tuples will be passed; the list will be iterated
            # through in order, and the tuple will get passed with the
            # extended call syntax,  self.setdefault(*data_tuple).
            log.debug("Initializing state data...")
            self.setdefault('org', '')
            self.setdefault('node', '')
            self.setdefault('service type', '')
            self.setdefault('service', '')
            self.setdefault('count', 0)
            self.setdefault('count ok', 0)
            self.setdefault('count warn', 0)
            self.setdefault('count error', 0)
            self.setdefault('count failed', 0)
            self.setdefault('current status', -1)
            self.setdefault('previous status', -1)
            self.setdefault('current status name', '')
            self.setdefault('previous status name', '')
            self.setdefault('desc', '')
            self.setdefault('data', '')
            self.setdefault('last check', '')
            self.setdefault('last ok', '')
            self.setdefault('last warn', '')
            self.setdefault('last error', '')
            self.setdefault('last failed', '')

    def backup(self):
        if not self.backup_file:
            log.err("The backup filename has not been set.")
        try:
            pickle.dump(self, open(self.backup_file,'w'))
            log.debug("State data has been written to %s." % self.backup_file)
        except IOError:
            log.err("Backup file does not exist; couldn't backup data.")

    def restore(self):
        if not self.backup_file:
            log.err("The backup filename has not been set.")
        try:
            saved_state = pickle.load(open(self.backup_file))
            log.msg("State data has been loaded from %s." % self.backup_file)
            self.update(saved_state)
        except Exception, e:
            log.err("Could not restore state: %s" % e)
        

class History(Queue, object):
    '''
    >>> h = History(3)
    >>> h.add('test 1')
    >>> h.queue
    ['test 1']
    >>> h.add('test 2')
    >>> h.queue
    ['test 1', 'test 2']
    >>> h.add('test 3')
    >>> h.queue
    ['test 1', 'test 2', 'test 3']
    >>> h.last
    Traceback (most recent call last):
    AttributeError: 'History' object has no attribute 'last'

    >>> h.add('test 4')
    >>> h.queue
    ['test 2', 'test 3', 'test 4']
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

def _test():
    import doctest, application
    doctest.testmod(application)

if __name__ == '__main__':
    _test()
