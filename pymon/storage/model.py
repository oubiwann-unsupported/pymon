"""
pymon storage module for the Storm ORM
"""

from datetime import datetime

from storm.databases.sqlite import SQLite
from storm.uri import URI
from storm.properties import Int, Unicode, DateTime
from storm.twisted.store import DeferredStore

from twisted.internet.defer import DeferredList

class Status(object):
    """
    Record for 'current status'
    """
    __storm_table__ = "status"
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    ok_count = Int()

class Event(object):
    """
    Record for a service's event
    """
    __storm_table__ = "event"
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    datetime = DateTime()
    transition = Unicode()
