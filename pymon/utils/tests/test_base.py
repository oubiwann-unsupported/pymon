from twisted.trial import unittest

from pymon.utils import base


class UtilsTestCase(unittest.TestCase):
    """
    """
    def test_isInList(self):
        input = [200, 303, 304, 401]
        self.assertTrue(base.isInList(200, input))
        self.assertTrue(base.isInList('200', input))
        self.assertFalse(base.isInList(405, input))
        self.assertFalse(base.isInList('405', input))
        input = '200, 303, 304, 401'
        self.assertTrue(base.isInList(200, input))
        self.assertTrue(base.isInList('200', input))
        self.assertFalse(base.isInList(405, input))
        self.assertFalse(base.isInList('405', input))
        input = ['200', '303', '304', '401']
        self.assertTrue(base.isInList(200, input))
        self.assertTrue(base.isInList('200', input))
        self.assertFalse(base.isInList(405, input))
        self.assertFalse(base.isInList('405', input))

    def test_isInNumericRange(self):
        self.assertTrue(base.isInNumericRange(1, '1-10'))
        self.assertTrue(base.isInNumericRange('1', '1-10'))
        self.assertTrue(base.isInNumericRange(5, '1-10'))
        self.assertTrue(base.isInNumericRange(10, '1-10'))
        self.assertFalse(base.isInNumericRange(0, '1-10'))
        self.assertFalse(base.isInNumericRange(11, '1-10'))
        self.assertFalse(base.isInNumericRange(100, '1-10'))

    def test_isInCharacterRange(self):
        self.assertTrue(base.isInCharacterRange('b', 'b-d'))
        self.assertTrue(base.isInCharacterRange('c', 'b-d'))
        self.assertTrue(base.isInCharacterRange('d', 'b-d'))
        self.assertFalse(base.isInCharacterRange('a', 'b-d'))
        self.assertFalse(base.isInCharacterRange('e', 'b-d'))
        self.assertFalse(base.isInCharacterRange('A', 'b-d'))
        self.assertFalse(base.isInCharacterRange('B', 'b-d'))
        self.assertFalse(base.isInCharacterRange('E', 'b-d'))

    def test_isInRange(self):
        self.assertTrue(base.isInRange(1, '1-10'))
        self.assertTrue(base.isInRange('1', '1-10'))
        self.assertFalse(base.isInRange(11, '1-10'))
        self.assertTrue(base.isInRange('a', 'a-z'))
        self.assertFalse(base.isInRange('A', 'a-z'))

    def test_isExactly(self):
        self.assertTrue(base.isExactly(1, 1))
        self.assertTrue(base.isExactly('1', '1'))
        self.assertTrue(base.isExactly(1, '1'))
        self.assertFalse(base.isExactly(1, 2))
        self.assertFalse(base.isExactly('1', '2'))
        self.assertFalse(base.isExactly(1, '2'))
        self.assertFalse(base.isExactly('1', 2))
    
    def test_getSimplePlural(self):
        self.assertEqual(base.getSimplePlural('word', 1), 'word')
        self.assertEqual(base.getSimplePlural('word', 2), 'words')
        self.assertEqual(base.getSimplePlural('word', 3), 'words')
        self.assertEqual(base.getSimplePlural('word', 100), 'words')
