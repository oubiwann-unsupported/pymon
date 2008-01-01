"""
pymon storage module for the Storm ORM
"""

from datetime import datetime

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
        from storm.databases import sqlite
        klass = sqlite.SQLite
    elif scheme == 'mysql':
        from storm.databases import mysql
        klass = mysql.MySQL
    elif scheme == 'postgres':
        from storm.databases import postgres
        klass = postgres.Postgres
    return klass(URI(connectionString))

def createTables(conn):
    conn.execute(sql.createStatusTable)
    conn.execute(sql.createEventTable)
    conn.execute(sql.createCountsTable)
    conn.execute(sql.createLastTimesTable)
    conn.execute(sql.createServiceTable)
    conn.commit()

def isTables(conn):
    try:
        conn.execute('SELECT * FROM status')
        return True
    # XXX this raw except needs to instead check for sqlite, mysql and postgres
    # table-not-found errors
    except:
        return False

def getStore(database=None, connectionString=''):
    if not database and connectionString:
        database = getDatabase(connectionString)
    # check to see if tables exist; if not, create them
    conn = database.connect()
    if not isTables(conn):
        createTables(conn)
    return DeferredStore(database)

def addHostStatus(host, service, data):
    pass

def updateHostStatus(host, service, data):
    pass

def addHostEvent(host, service, data):
    pass

