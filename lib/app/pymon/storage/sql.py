import inspect

from sqlobject import SQLObject
from sqlobject import IntCol, StringCol, DateCol
from sqlobject.sqlite import builder

from adytum.app.pymon.api import config

states = config.pymon.getStateDefs()
lookup = dict(zip(states.values(), states.keys()))

#################
# database setup
#################
# check to see if we got called from _test()
stack = [ x[3] for x in inspect.stack() ]
    
# this is most likely very fragile; this was arrived at
# through trial and error
if '_test' in stack or len(stack) == 1:
    # get test db info
    proto = config.pymon.sections['test database']['type']
    dbpath = config.pymon.sections['test database']['location']
    dbname = config.pymon.sections['test database']['name']
else:
    # get real db data
    proto = config.pymon.sections['database']['type']
    dbpath = config.pymon.sections['database']['location']
    dbname = config.pymon.sections['database']['name']



db = builder()
conn = db.connectionFromURI('%s://%s/%s' % (proto, dbpath, dbname))
conn.autoCommit = True

def buildUniqID(data):
    return '%s|%s|%s' % (data['serviceHost'], 
        data['serviceType'], data['serviceName'])
    
#################
# table setup
#################
class Service(SQLObject):
    '''
    Setup some constants
    >>> OK=1
    >>> RECOVERING=2
    >>> WARN=3
    >>> ERROR=4

    Create some test data
    >>> data = {
    ...     'serviceHost': 'capawl01',
    ...     'serviceType': 'local process',
    ...     'serviceName': 'httpd',
    ...     'serviceStatus': OK,
    ...     'serviceMessage': 'There were 11 httpd processes',
    ...     'previousState': WARN,
    ...     'lastChecked': '2004-08-17 03:40:00',
    ...     'lastOK': '2004-08-17 03:40:00',
    ...     'lastWarn': '2004-08-16 03:40:00',
    ...     'lastError': '2004-08-15 03:40:00',
    ... }
    >>> data.update({'uniqueID': buildUniqID(data)}) 

    Test an insert
    >>> s = Service(**data)

    Test a non-unique insert
    >>> try:
    ...     s = Service(**data)
    ... except Exception, e:
    ...     print e
    column unique_id is not unique

    Test SELECT
    >>> svs = Service.select()
    >>> for svc in svs:
    ...    print '%s - %s - %s: %s' % (svc.serviceHost, svc.serviceType,
    ...        svc.serviceName, svc.serviceStatus)
    capawl01 - local process - httpd: 1

    Removed the database
    >>> import os
    >>> db = os.path.join(dbpath, dbname)
    >>> os.unlink(db)
    '''

    _connection = conn

    uniqueID = StringCol(unique=True)
    serviceHost = StringCol()
    serviceType = StringCol()
    serviceName = StringCol()
    serviceStatus = IntCol()
    serviceMessage = StringCol()
    previousState = IntCol(default=None)
    lastChecked = DateCol(default=None)
    lastOK = DateCol(default=None)
    lastWarn = DateCol(default=None)
    lastError = DateCol(default=None)

# Setup database on import
#Service.dropTable()
Service.createTable(ifNotExists=True)



def updateDatabase(data):
    '''
    Convenience function for updating monritor data.
        
    Will be replaced soon.
    '''

    uid = data['uniqueID']
    select = Service.select(Service.q.uniqueID==uid)
    #print select
    #print select.count()
    if not select.count():
        insert = Service(**data)
        print "Inserting data..."
    else:
        r = select[0]
        prev = r.serviceStatus
        curr = data['serviceStatus']
        if curr == states['ok'] and prev != states['ok'] and prev != states['recovering']:
            curr = states['recovering']
        lastO = r.lastOK
        lastW = r.lastWarn
        lastE = r.lastError
        update = {
            'serviceStatus': curr,
            'serviceMessage': data['serviceMessage'],
            'previousState': prev,
            'lastOK': lastO,
            'lastWarn': lastW,
            'lastError': lastE,
        }
        print "Updating data..."
        r.set(**update)
        print "Getting results for %s:" % uid
        print "Previous state: %s" % lookup[str(r.previousState)].upper()
        print "Current state: %s" % lookup[str(r.serviceStatus)].upper()

def _test():
    import doctest, datamodel
    return doctest.testmod(datamodel)

if __name__ == '__main__':
    _test()

