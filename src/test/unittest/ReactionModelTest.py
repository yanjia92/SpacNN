# -*- coding: utf-8 -*-
from CheckerTest import CheckerTestBase


class ReactionModelTest(CheckerTestBase):
    def _get_model_name(self):
        return "reaction"

    def _get_ltl(self):
        return "true U[10, 10] naeq5"

    def _get_duration(self):
        return 10

    def _get_samples(self):
        return 1000

    def testCheckCorrect(self):
        '''
        验证当cntNa=10, cntCl=10时，上述ltl公式验证的结果和prism的相等(0.2460859)
        :return:
        '''
        prism_result = 0.2460859
        self.assertAlmostEqual(self._checker.run_checker(), prism_result, delta=0.01)

