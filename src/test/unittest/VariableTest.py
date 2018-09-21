import unittest
from module.Module import BoundedVariable
from copy import copy


class VariableTest(unittest.TestCase):
    def setUp(self):
        self.varobj = BoundedVariable("i", 0, range(3), int, True)
        self.copied = copy(self.varobj)

    def testCopy(self):
        self.assertNotEqual(id(self.varobj), id(self.copied))
        self.copied.set_value(1)
        self.assertEqual(self.varobj.get_value(), 0)
        self.assertEqual(self.copied.get_value(), 1)