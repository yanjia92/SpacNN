from unittest import TestCase
from checker.LTLChecker import LTLChecker
from module.AnotherStep import AnotherStep as Step


class LTLCheckerTest(TestCase):
    def setUp(self):
        def lbl_mapper(vars_map):
            if vars_map['a'] == 1:
                return 'aeq1'
            else:
                return 'aneq1'
        self._lbl_mapper = lbl_mapper
        self._parsed_LTL1 = ["U[0.0, 0.5]", 'true', 'aeq1']  # False
        self._parsed_LTL2 = ["U[0.0, 1.5]", 'true', 'aeq1']  # True
        self._checker = LTLChecker()

    def testCheckUntil(self):
        checker = self._checker
        path1 = []
        step1 = Step({'a':0}, 0.0, 1.0, self._lbl_mapper)
        step2 = Step({'a':1}, 1.0, 2.0, self._lbl_mapper)
        path1.append(step1)
        path1.append(step2)
        self.assertFalse(checker.check(path1, self._parsed_LTL1))
        self.assertTrue(checker.check(path1, self._parsed_LTL2))




