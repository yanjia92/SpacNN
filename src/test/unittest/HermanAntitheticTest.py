# -*- coding:utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase


class HermanAntitheticTest(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)

    def _get_model_name(self):
        return "herman7"

    def _get_ltl(self):
        return "true U<=5 stable"

    def _get_sample_size(self):
        return 400

    def testCheckingCorrect(self):
        '''
        测试checker验证 true U<=5 stable的概率约等于0.6418
        :return:
        '''
        checker = self._get_checker()
        result = checker.run_checker()
        self.assertAlmostEqual(result, 0.6418, delta=0.02)