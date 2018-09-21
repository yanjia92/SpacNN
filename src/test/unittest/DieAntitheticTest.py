# -*- coding:utf-8 -*-
from CheckerTest import CheckerTestBase
import matplotlib.pyplot as plt
from util.MathUtils import *


class DieTest(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)

    def _get_model_name(self):
        return "die"

    def _get_sample_size(self):
        return 400

    def _get_ltl(self):
        return "true U<=10 result_45"

    def testChecking(self):
        checker = self._get_checker()
        print checker.run_checker()

    def testCheckAntithetic(self):
        checker = self._get_checker()
        paths, results = checker.check_and_export(1000)
        checker.rearrange(paths, results)
        checker.set_antithetic(True)
        print checker.run_checker()

    def testVarReduction(self):
        samples = 50
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance = sum([(check_result - average) ** 2 for check_result in check_results])

        self._checker.antithetic = True
        check_results = [self._checker.run_checker() for _ in range(samples)]
        average = sum(check_results) / len(check_results)
        variance1 = sum([(check_result - average) ** 2 for check_result in check_results])

        print variance
        print variance1

    def _get_sample(self, sample_size, antithetic=False):
        '''
        返回sample_size条路径的验证结果
        :param sample_size: sample_size
        :param antithetic:
        :return: list of number(0/1)
        '''
        checker = self._get_checker()
        _, results = checker.check_and_export(sample_size, antithetic=antithetic)
        return map(lambda elem: [0, 1][elem], results)

    def testShowRelativeIndex(self):
        '''
        展示使用对偶路径和不使用对偶路径的100个样本的内部相关系数的直方图
        :return:
        '''
        checker = self._get_checker()
        sample_size = 400
        sample_cnt = 100
        samples = [self._get_sample(sample_size) for _ in range(sample_cnt)]
        paths, results = checker.check_and_export(200)
        checker.rearrange(paths, results)
        anti_samples = [self._get_sample(sample_size, antithetic=True) for _ in range(sample_cnt)]
        # 相关系数
        indexs = [rel_index(sample[0::2], sample[1::2]) for sample in samples]
        anti_indexs = [rel_index(anti_sample[0::2], anti_sample[1::2]) for anti_sample in anti_samples]
        plt.subplot(121)
        plt.hist(indexs, 10)
        plt.subplot(122)
        plt.hist(anti_indexs, 10)
        plt.show()

    def testShowVariance(self):
        '''
        证明对偶路径产生的样本的方差（而非样本方差）较小
        :return:
        '''
        variance_cnt = 100  # 统计100次 估计值的方差
        variance_size = 10  # 为了求估计值的方差需要进行10次模型验证
        sample_size = 400  # 为了进行一次模型验证需要取得400次随机路径
        variances = []
        for _ in range(variance_cnt):
            samples = [self._get_sample(sample_size) for _ in range(variance_size)]
            check_results = map(lambda sample: sum(sample) / float(len(sample)), samples)
            variances.append(variance(check_results))

        checker = self._get_checker()
        paths, results = checker.check_and_export(sample_size)
        checker.rearrange(paths, results)
        anti_variances = []
        for _ in range(variance_cnt):
            samples = [self._get_sample(sample_size, antithetic=True) for _ in range(variance_size)]
            check_results = map(lambda sample: sum(sample) / float(len(sample)), samples)
            anti_variances.append(variance(check_results))

        plt.subplot(121)
        plt.hist(variances, bins=20)
        plt.subplot(122)
        plt.hist(anti_variances, bins=20)
        plt.show()