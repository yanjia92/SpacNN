# -*- coding:utf-8 -*-

from CheckerTest import CheckerTestBase


class QueueNetworkTest(CheckerTestBase):
    '''
    测试工具对于queue_network.prism模型的正确性
    '''

    def setUp(self):
        CheckerTestBase.setUp(self)
        self._checker.antithetic = True

    def _get_model_name(self):
        return "queue_network"

    def _get_sample_cnt(self):
        return 200

    def _get_ltl(self):
        return "true U<=50 full"

    def testCheckCorrect(self):
        prism_answer = 0.086023
        delta = 0.02
        check_answer = self._checker.run_checker()
        self.assertAlmostEqual(prism_answer, check_answer, delta=delta)

    def testVarReduction(self):
        samples = 10
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance = sum([(check_result - average) ** 2 for check_result in check_results])

        self._checker.antithetic = True
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance1 = sum([(check_result - average) ** 2 for check_result in check_results])

        print variance
        print variance1