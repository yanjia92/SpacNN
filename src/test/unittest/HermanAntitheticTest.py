# -*- coding:utf-8 -*-
from test.unittest.AntitheticTestBase import AntitheticTestCase


class HermanAntitheticTest(AntitheticTestCase):
    def setUp(self):
        AntitheticTestCase.setUp(self)

    def _get_model_name(self):
        return "herman7"

    def _get_ltl(self):
        return "true U<=5 stable"

    def _get_sample_size(self):
        return 200

    def _get_rearrange_path_cnt(self):
        return 10000

    def _get_variance_cnt(self):
        return 100

    def _get_variance_size(self):
        return 10

    def testCheckingCorrect(self):
        '''
        测试checker验证 true U<=5 stable的概率约等于0.6418
        :return:
        '''
        self.assertAlmostEqual(self._get_checker().run_checker(), 0.6418, delta=0.02)

    def testCheckCorrectAntithetic(self):
        checker = self._get_checker()
        paths, results = checker.check_and_export(self._get_rearrange_path_cnt())
        checker.rearrange(paths, results)
        checker.set_antithetic(True)
        self.assertAlmostEqual(checker.run_checker(), 0.6418, delta=0.1)

    def testCheckAntithetic(self):
        '''
        验证对偶路径方法能够减小相关系数
        :return:
        '''
        checker = self._get_checker()
        paths, results = checker.check_and_export(1000)
        checker.rearrange(paths, results)
        checker.set_antithetic(True)
        self.assertAlmostEqual(checker.run_checker(), 0.6418, delta=0.02)

    def testShowRelativeIndex(self):
        '''
        展示使用对偶路径和不使用对偶路径的100个样本的内部相关系数的直方图
        :return:
        '''
        self._showRelativeIndex()

    def testShowVariance(self):
        '''
        分别对使用对偶路径和不使用对偶路径统计100次估计值的方差，画出直方图
        :return:
        '''
        self._showVariance()