# Copyright (c) 2007 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test for twistorm.
"""

import os
from datetime import datetime

from storm.databases.sqlite import SQLite
from storm.uri import URI
from storm.twisted.store import DeferredStore

from twisted.trial.unittest import TestCase
from twisted.internet.defer import DeferredList

from pymon.storage import sql
from pymon.storage import api
from pymon.storage.model import Status, Event

class DatabaseSetupTestCase(TestCase):
    """
    Tests for L{DeferredStore}.
    """

    def setUp(self):
        """
        Create a test sqlite database, and insert some data.
        """
        self.filename = self.mktemp()

    def test_createTables(self):
        pass

    def test_checkTables(self):
        pass
        self.filename = self.mktemp()
        self.database = api.getDatabase("sqlite:" + self.filename)
        conn = self.database.connect()
        api.createTables(conn)
        # XXX make assertions about tables

class DatabaseAPITestCase(TestCase):
    """

    """

    def setUp(self):
        """
        Create a test sqlite database, and insert some data.
        """
        self.filename = self.mktemp()
        self.database = api.getDatabase("sqlite:" + self.filename)
        self.host = u'www.adytum.us'
        self.service = u'ping'
        self.events = [u'warning', u'recovering', u'ok', u'error']
        conn = self.database.connect()
        api.createTables(conn)
        self.store = api.getStore(self.database)
        return self.store.start()

    def createHostStatus(self):
        stat = Status()
        stat.host = self.host
        stat.service = self.service
        stat.ok_count = 0
        return self.store.add(stat)

    def createHostEvent(self, transition, datetime):
        event = Event()
        event.host = self.host
        event.service = self.service
        event.transition = transition
        event.datetime = datetime
        return self.store.add(event)

    def queryHostStatus(self, result, host=None):
        if not host:
            host = self.host
        return self.store.find(Status, Status.host==host)

    def cbGetOneResult(self, results):
        return results.one()

    def cbGetAllResults(self, results):
        return results.get_all()

    def tearDown(self):
        """
        Kill the store (and its underlying thread).
        """
        os.remove(self.filename)
        return self.store.stop()

    def test_addStatus(self):
        """
        Add an object to the store.
        """
        def cbCheck(result):
            self.assertEquals(result.host, self.host)
            self.assertEquals(result.service, self.service)
            return result
        d = self.createHostStatus()
        d.addCallback(self.queryHostStatus)
        d.addCallback(self.cbGetOneResult)
        d.addCallback(cbCheck)
        return d

    def test_incrementCount(self):
        """
        Let's update the count attribute and then check to see that this has
        persisted.
        """
        def cbSetCount(stat):
            stat.ok_count += 1
            return self.store.commit()
        def cbCheckIncrement(stat):
            self.assertEquals(stat.ok_count, 1)
            return stat
        d = self.createHostStatus()
        d.addCallback(self.queryHostStatus)
        d.addCallback(self.cbGetOneResult)
        d.addCallback(cbSetCount)
        d.addCallback(self.queryHostStatus)
        d.addCallback(self.cbGetOneResult)
        d.addCallback(cbCheckIncrement)
        return d

    def test_addEvent(self):
        """
        Let's put stuff in the history table and see that the data persisted.
        """
        def cbQueryEvent(ign):
            return self.store.find(Event).addCallback(self.cbGetAllResults)

        def cbCheckEvent(events):
            # XXX uncomment when storm.twisted supports order_by
            #events.order_by(Event.datetime)
            expected = self.events
            received = [x.transition for x in events]
            self.assertEqual(expected, received)
        def createEvents():
            dl = []
            for event in self.events:
                dl.append(self.createHostEvent(event, datetime.now()))
            return DeferredList(dl)
        d = createEvents()
        d.addCallback(cbQueryEvent)
        d.addCallback(cbCheckEvent)
        return d
