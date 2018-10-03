# -*- coding:utf-8 -*-
from test.unittest.AntitheticTestBase import AntitheticTestCase
from util.MathUtils import variance


class BroadcastAntitheticTest(AntitheticTestCase):

    def setUp(self):
        AntitheticTestCase.setUp(self)
        self.check_answer = 0.475329792
        self.check_delta = 0.05

    def _get_model_name(self):
        return "broadcast9"

    def _get_ltl(self):
        return "true U<=10 node8receive"

    def _get_sample_size(self):
        return 600

    def _get_rearrange_path_cnt(self):
        return 3000

    def testCheckingCorrect(self):
        '''
        验证模型满足公式的概率基本正确
        :return:
        '''
        self.assertAlmostEqual(self._get_check_result(), self.check_answer, delta=self.check_delta)

    def testCheckCorrectAntithetic(self):
        '''
        验证对偶路径验证结果正确
        :return:
        '''
        return self.assertAlmostEqual(self._get_checker().run_anti_smc(3000, None), self.check_answer, delta=self.check_delta)

    def testExperiment(self):
        '''
        使用标准SMC和对偶路径SMC，返回10次运算结果
        :return:
        '''
        checker = self._get_checker()
        results = [checker.run_smc() for _ in range(10)]
        self._rearrange()
        checker.set_antithetic(True)
        anti_results = [checker.run_smc() for _ in range(10)]
        print "SMC"
        for r in results:
            print r
        print "antithetic SMC"
        for anti_r in anti_results:
            print anti_r

    def testShowRelativeIndex(self):
        self._showRelativeIndex()

    def testShowVariance(self):
        self._showVariance()

    def testCompareVariance(self):
        '''
        两种SMC算法各取100个样本，比较方差大小
        :return:
        '''
        checker = self._get_checker()
        results = [checker.run_smc() for _ in range(100)]
        anti_results = [checker.run_anti_smc(3000) for _ in range(100)]
        print variance(results)
        print variance(anti_results)


