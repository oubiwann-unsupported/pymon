import os

from twisted.trial import unittest

import yaml

from pymon import config
from pymon.testing import utils


class ConfigTestCase(unittest.TestCase):
    """
    """


class ConfigMainTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.rawMainConfig = utils.loadGeneralYAML()
        self.config = config.ConfigMain(self.rawMainConfig)

    def test_getPymonUserGroup(self):
        userData, groupData = self.config.getPymonUserGroup()
        self.assertEqual(userData.pw_gecos, "Unprivileged User")
        self.assertEqual(groupData.gr_name, "nobody")

    def test_getStateNames(self):
        states = self.config.getStateNames()
        expected = [
            'acknowledged', 'disabled', 'error', 'escalated', 'failed',
            'maintenance', 'ok', 'recovering', 'unknown', 'warn'
            ]
        self.assertEqual(states, expected)

    def test_getStateNumbers(self):
        states = self.config.getStateNumbers()
        expected = [-1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        self.assertEqual(states, expected)

    def test_getStateNameFromNumber(self):
        self.assertEqual(self.config.getStateNameFromNumber(20), 'error')
        self.assertEqual(self.config.getStateNameFromNumber(70), 'ok')
        self.assertEqual(self.config.getStateNameFromNumber(30), 'warn')

    def test_getStateNumberFromName(self):
        self.assertEqual(self.config.getStateNumberFromName('error'), 20)
        self.assertEqual(self.config.getStateNumberFromName('ok'), 70)
        self.assertEqual(self.config.getStateNumberFromName('warn'), 30)


class ConfigMonitorTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.rawMonitorsConfig = utils.loadMonitorYAML()


class ConfigAPITestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        self.rawMainConfig = utils.loadGeneralYAML()
        self.rawMonitorsConfig = utils.loadMonitorYAML()
        self.config = config.ConfigAPI(
            self.rawMainConfig, self.rawMonitorsConfig)

    def test_create(self):
        self.assertTrue(self.config.main is not None)
        self.assertTrue(self.config.monitors is not None)
