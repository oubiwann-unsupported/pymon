"""
pymon storage module for the Storm ORM
"""
from datetime import datetime

from storm.databases.sqlite import SQLite
from storm.uri import URI
from storm.properties import Int, Unicode, DateTime, RawStr
from storm.twisted.store import DeferredStore

from twisted.internet.defer import DeferredList


class Service(object):
    """
    Record for monitored service; this is host information and should change
    infrequently (if at all) for steady-state networks. This information is
    used by pymon more as a lookup table than anything else.
    """
    # XXX make hostname + service unique
    __storm_table__ = 'services'
    id = Int(primary=True)
    org = Unicode()
    host = Unicode()
    service = Unicode()
    service_type = Unicode()
    factory = RawStr()
    config = RawStr()


class Status(object):
    """
    Record for 'current status'
    """
    # XXX add relation for service
    __storm_table__ = "status"
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    current = Int()
    current_name = Unicode()
    previous = Int()
    previous_name = Unicode()
    message = Unicode()
    data = Unicode()


class Counts(object):
    """
    Record for total number of checks in each of the pymon states.
    """
    # XXX add relation for service
    __storm_table__ = 'counts'
    ok = Int()
    warn = Int()
    error = Int()
    failed = Int()
    unknown = Int()
    maintenance = Int()
    disabled = Int()


class LastTimes(object):
    """
    Record for tracking the last time a service was in any given state.
    """
    __storm_table__ = 'last_times'
    check = DateTime()
    ok = DateTime()
    warn = DateTime()
    error = DateTime()
    failed = DateTime()


class Event(object):
    """
    Record for a service's status transitions
    """
    # XXX add relation for service
    __storm_table__ = "events"
    id = Int(primary=True)
    host = Unicode()
    service = Unicode()
    current = Int()
    current_name = Unicode()
    previous = Int()
    previous_name = Unicode()
    message = Unicode()
    data = Unicode()
