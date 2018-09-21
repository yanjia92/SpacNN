# -*- coding: utf-8 -*-
from CheckerTest import CheckerTestBase


class ReactionModelTest(CheckerTestBase):

    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _get_model_name(self):
        return "reaction"

    def _get_ltl(self):
        return "true U[0.001, 0.001] naeq5"

    def _get_duration(self):
        return 0.001

    def _get_sample_size(self):
        return 2000

    def testCheckCorrect(self):
        '''
        验证当cntNa=10, cntCl=10时，上述ltl公式验证的结果和prism的相等
        :return:
        '''
        prism_result = 0.32252
        check_result = self._checker.run_checker()
        print "Check result:{}".format(check_result)
        self.assertAlmostEqual(check_result, prism_result, delta=0.01)


    def testComputeVar(self):
        '''
        计算100次估计值的方差
        :return:
        '''
        check_results = []
        samples = 200
        for _ in range(samples):
            check_results.append(self._checker.run_checker())
        average = sum(check_results) / samples
        quad_error = sum([(result - average) ** 2 for result in check_results]) / samples

        self._checker.antithetic = True
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / samples
        quad_error1 = sum([(result - average) ** 2 for result in check_results]) / samples

        print quad_error
        print quad_error1