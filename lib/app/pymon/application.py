from Queue import Queue
try:
    import cPickle as pickle
except:
    import pickle

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
    >>> os.unlink(s.getBackupFilename())
    >>> os.path.exists(s.getBackupFilename())
    False
    '''
    def __init__(self, use_globalRegistry=True):
        import os
        if not use_globalRegistry:
            self.setBackupFilename(None)
        else:
            from registry import globalRegistry
            try:
                cfg = globalRegistry.config.system.backups.state_data
                self.filename = os.path.join(cfg.directory, cfg.filename)
                self.setBackupFilename(self.filename)
            except AttributeError:
                self.setBackupFilename(None)
            self.filename = self.getBackupFilename()
            if self.filename:
                if os.path.exists(self.filename):
                    self.restore()
                    os.unlink(self.filename)
        self.setdefault('last status', -1)
        self.setdefault('current status', -1)


    def setBackupFilename(self, filename):
        self.backup_file = filename

    def getBackupFilename(self):
        return self.backup_file

    def backup(self):
        if not self.getBackupFilename():
            raise StateBackupError, "The backup filename has not been set."
        pickle.dump(self, open(self.backup_file,'w'))

    def restore(self):
        if not self.getBackupFilename():
            raise StateBackupError, "The backup filename has not been set."
        saved_state = pickle.load(open(self.backup_file))
        self.update(saved_state)
        

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
