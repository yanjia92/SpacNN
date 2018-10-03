from util.Geometry import *
from unittest import TestCase


class GeometryTest(TestCase):

    def setUp(self):
        self.k = 1
        self.b = 1
        self.line_func = self._generate_line(self.k, self.b)
        self.points = [(0, 0)]
        self.distances = [sqrt(2)/2.0]

    def testPoint2Line(self):
        for p, d in zip(self.points, self.distances):
            x, y = p
            self.assertAlmostEqual(point_2_line(x, y, self.line_func), d, delta=0.01)

    def _generate_line(self, k, b):
        def func(x):
            return k*x + b
        return func