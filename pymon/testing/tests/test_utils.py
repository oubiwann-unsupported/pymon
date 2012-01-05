import os

from twisted.trial import unittest

from pymon.testing import utils


class TestingUtilsTestCase(unittest.TestCase):
    """
    """
    def test_getDataDir(self):
        absPath = utils.getDataDir()
        partial = os.path.sep.join(absPath.split(os.path.sep)[-3:])
        self.assertEqual(partial, "pymon/testing/data")

    def test_loadGeneralYAML(self):
        data = utils.loadGeneralYAML()
        expected = [
            'admin', 'agents', 'check by', 'daemon name',
            'daemontools enabled', 'daemontools service', 'database',
            'install prefix', 'instance name', 'log level', 'mail from',
            'monitor status', 'notifications', 'peers', 'sendmail',
            'smtp password', 'smtp port', 'smtp server', 'smtp username',
            'state definitions', 'system group', 'system user',
            'user agent string', 'web service']
        self.assertEqual(sorted(data.keys()), expected)

    def test_loadMonitorYAML(self):
        data = utils.loadMonitorYAML()
        expected = ['services']
        self.assertEqual(sorted(data.keys()), expected)
