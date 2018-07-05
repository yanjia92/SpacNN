# -*- coding: utf-8 -*-
import unittest
from util.StringUtil import StringUtil


class Test(unittest.TestCase):
    def test_is_num(self):
        positive_cases = []
        negative_cases = []
        positive_cases.append("123")
        positive_cases.append("123.123")
        negative_cases.append("affgaf")
        negative_cases.append(" ")
        negative_cases.append("")
        for positive_case, negative_case in zip(positive_cases, negative_cases):
            self.assertTrue(StringUtil.isnum(positive_case))
            self.assertFalse(StringUtil.isnum(negative_case))

