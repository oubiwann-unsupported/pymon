"""
pymon storage API.
"""

from datetime import datetime

import txmongo

from pymon.config import cfg


def getConnection(connectionString=''):
    if not connectionString:
        connectionString = cfg.database.connectionString
    parts = connectionString.split(':')
    scheme = parts[0]
    if scheme == 'mongo':
        # XXX take all these parameters from the connection string + query
        # params
        deferred = txmongo.MongoConnectionPool(
            host="localhost", port=27017, reconnect=True, pool_size=5)
    return deferred


# XXX this is experimental/propositional... and untested so far!
def updateConfigSection(sectionName, newData):
    
    def _eb(failure):
        # XXX do something better here!
        print failure

    # XXX the code in these callbacks should go in a
    # pymon.storage.backend.mongo module ... once we've done a few more and the
    # patterns have properly emerged.
    def _cb(connection):
        # XXX get database name from the connection string + query params
        db = getattr(connection, "pymon")
        collection = getattr(db, "config")
        # XXX get data by section name
        deferred = collection.update({"section": sectionName}, newData)
        # XXX add a callback? maybe writing to the log?
        #deferred.addCalback(logit)
        deferred.addErrback(_eb)
        return deferred

    deferred = getConnection()
    deferred.addCallback(_cb)
    return deferred


def updateConfigSubSection(sectionName, subSectionName, newdata):
    pass


def addHostStatus(host, service, data):
    pass


def updateHostStatus(host, service, data):
    pass


def addHostEvent(host, service, data):
    pass
