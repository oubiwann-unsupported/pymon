"""
pymon storage module for the Storm ORM
"""

from datetime import datetime

from storm import databases
from storm.uri import URI
from storm.properties import Int, Unicode, DateTime
from storm.twisted.store import DeferredStore

from twisted.internet.defer import DeferredList

from pymon.storage import sql
from pymon.config import cfg

def getDatabase(connectionString=''):
    if not connectionString:
        connectionString = cfg.database.connectionString
    parts = connectionString.split(':')
    scheme = parts[0]
    if scheme == 'sqlite':
        return databases.sqlite.SQLite(URI(connectionString))
    elif scheme == 'mysql':
        return databases.mysql.MySQL(URI(connectionString))
    elif scheme == 'postgres':
        return databases.postgres.Postgres(URI(connectionString))

def getStore(database=None, connectionString=''):
    if database:
        return DeferredStore(database)
    elif connectionString:
        db = getDatabase(connectionString)
        return DeferredStore(db)

def createTables(conn):
    conn.execute(sql.createStatusTable)
    conn.execute(sql.createEventTable)
    conn.commit()

def checkTables(conn):
    pass

def addHostStatus(host, service, data):
    pass

def updateHostStatus(host, service, data):
    pass

def addHostEvent(host, service, data):
    pass

