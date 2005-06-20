from ZODB import FileStorage, DB
from ZEO import ClientStorage
from BTrees.OOBTree import OOBTree
import sys
sys.path.append('/usr/local/ZopeX3-3.0.0/lib/python/')
from persistent import Persistent
from pprint import pformat

class ServiceRow(Persistent):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.description = ''
        self.organization = ''
        self.service = ''
        self.hostname = ''
        self.count = 0
        self.state_current = ''
        self.state_last = ''
        self.time_lastcheck = ''
        self.time_lastok = ''
        self.time_lastwarn = ''
        self.time_lasterror = ''

    def wx_str(self):
        #return 'I want to paint his yoohoo... goOOoold.'
        return pformat(self.__dict__)

class ServiceTransitions(Persistent):
    def __init__(self):
        self.id = ''
        self.organization = ''
        self.hostname = ''
        self.service = ''
        self.transition_status_start = ''
        self.transition_status_end = ''
        self.transition_time_start = ''
        self.transition_time_end = ''

    def wx_str(self):
        #return 'I want to paint his yoohoo... goOOoold.'
        return pformat(self.__dict__)


if __name__ == '__main__':

    ZEO=True
    # setup the data store
    if ZEO:
        server = 'localhost'
        port = 999
        storage = ClientStorage.ClientStorage((server, port))
    else:
        storage = FileStorage.FileStorage('data/zodb/pymondb.fs')
    db = DB(storage)
    conn = db.open()
    dbroot = conn.root()
    state_table = 'monitoring_states'
    transition_table = 'monitoring_transitions'

    # setup the state table for usage/insert
    dbroot[state_table] = OOBTree()
    mondb = dbroot[state_table]

    mon = ServiceRow()
    mon.id = 'myserver.hostingcompany.com-httpd' 
    mon.name = 'Apache Web Server'
    mon.description = 'This is the staging Web Server Service for 16 low-volume clients'
    mon.organization = 'My Special Client'
    mon.service = 'httpd'
    mon.hostname = 'myserver.hostingcompany.com'
    mon.state_current = 'OK'
    mon.state_last = 'OK'
    mondb[mon.id] = mon
    get_transaction().commit()

    # setup the transition table for usage/insert
    dbroot[transition_table] = OOBTree()
    mondb = dbroot[transition_table]

    trans = ServiceTransitions()
    trans.id = 'myserver.hostingcompany.com-httpd-2005.04.11.15:58:32'
    trans.organization = 'My Special Client'
    trans.hostname = 'myserver.hostingcompany.com'
    trans.service = 'httpd'
    trans.transition_status_start = ''
    trans.transition_status_end = ''
    trans.transition_time_start = ''
    trans.transition_time_end = ''
    mondb[trans.id] = trans
    get_transaction().commit()


