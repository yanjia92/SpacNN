from checker.Checker import BoundedInterval as Interval
from unittest import TestCase


class IntervalTest(TestCase):
    def testOverlap(self):
        i1 = Interval(0, 1)
        i2 = Interval(1, 2)
        i3 = Interval(0.5, 1)
        self.assertTrue(i1.overlap_with(i1))
        self.assertTrue(i1.overlap_with(i3))
        self.assertFalse(i1.overlap_with(i2))