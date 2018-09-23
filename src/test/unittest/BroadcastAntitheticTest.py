# -*- coding:utf-8 -*-
from test.unittest.AntitheticTestBase import AntitheticTestCase


class BroadcastAntitheticTest(AntitheticTestCase):
    def _get_model_name(self):
        return "broadcast"

    def _get_ltl(self):
        return "true U<=10 node3receive"

    def _get_sample_size(self):
        return 20

    def _get_rearrange_path_cnt(self):
        return 3000

    def testCheckingCorrect(self):
        '''
        验证模型满足公式的概率为0.585542
        :return:
        '''
        self.assertAlmostEqual(self._get_check_result(), 0.585542, delta=0.02)

    def testCheckCorrectAntithetic(self):
        '''
        验证对偶路径验证结果正确
        :return:
        '''
        return self.assertAlmostEqual(self._get_antithetic_check_result(), 0.585542, delta=0.02)

    def testShowRelativeIndex(self):
        self._showRelativeIndex()

    def testShowVariance(self):
        self._showVariance()
