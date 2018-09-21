# -*- coding:utf-8 -*-
from unittest import TestCase
from module.Step import Step
from module.NextMove import NextMove
from checker.Checker import Checker


class CheckerUnittest(TestCase):

    def setUp(self):
        self._checker = Checker(None)
        self.parsed_ltl1 = ["U[1, 2]", "true", "ap1"]
        self.parsed_ltl2 = ["U[2, 2]", "true", "ap1"]
        self.parsed_ltl3 = ["U[3, 3]", "true", "ap1"]
        self.parsed_ltl4 = ["U[0.001, 0.001]", "true", "ap1"]
        self.parsed_ltl5 = ["U[0.002, 0.002]", "true", "ap1"]
        self.parsed_ltl6 = ["U[0.003, 0.003]", "true", "ap1"]

        apsets = [{"a"}, {"ap1"}]
        next_moves = [
            NextMove(0, 1, None, 1.0, 1.0),
            NextMove(1, 1, None, 1.0, 1.0)
        ]
        next_moves1 = [
            NextMove(0.0, 0.001, None, 1.0, 1.0),
            NextMove(0.001, 0.001, None, 1.0, 1.0)
        ]
        self.path = [Step(apset, move) for apset, move in zip(apsets, next_moves)]
        self.path1 = [Step(_apset, _move) for _apset, _move in zip(apsets, next_moves1)]

    def testCheckUntil(self):
        self.assertTrue(self._checker.verify(self.path, self.parsed_ltl1))
        self.assertTrue(self._checker.verify(self.path, self.parsed_ltl2))
        self.assertFalse(self._checker.verify(self.path, self.parsed_ltl3))

        self.assertTrue(self._checker.verify(self.path1, self.parsed_ltl4))
        self.assertTrue(self._checker.verify(self.path1, self.parsed_ltl5))
        self.assertFalse(self._checker.verify(self.path1, self.parsed_ltl6))