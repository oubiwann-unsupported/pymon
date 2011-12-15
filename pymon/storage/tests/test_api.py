# Copyright (c) 2007 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for storage API.
"""

import os
from datetime import datetime

from twisted.trial.unittest import TestCase
from twisted.internet.defer import DeferredList

from pymon.storage import api


class DatabaseSetupTestCase(TestCase):
    """
    Tests for the part of L{pymon.storage.api} that deals with getting a
    database from a connection string, creating tables, and getting a store.
    """

    def setUp(self):
        """
        Create a test database, and insert some data.
        """
        self.filename = self.mktemp()

    def test_connectionSchema(self):
        db = api.getDatabase("mongo:")


class DatabaseAPITestCase(TestCase):
    """

    """
    def setUp(self):
        """
        Create a test "database", and insert some data.
        """
        self.filename = self.mktemp()
        self.database = api.getDatabase("mongo:" + self.filename)
        self.host = u'www.adytum.us'
        self.service = u'ping'
        self.events = [u'warning', u'recovering', u'ok', u'error']
        self.conn = self.database.connect()

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
        results.order_by(Event.datetime)
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
            d = self.store.find(Event)
            d.addCallback(self.cbGetAllResults)
            return d

        def cbCheckEvent(events):
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
