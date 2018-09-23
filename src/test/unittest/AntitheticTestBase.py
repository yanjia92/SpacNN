# -*- coding:utf-8 -*-
from test.unittest.CheckerTest import CheckerTestBase
from util.MathUtils import *
import matplotlib.pyplot as plt


class AntitheticTestCase(CheckerTestBase):
    def setUp(self):
        CheckerTestBase.setUp(self)

    def _get_sample(self, size, antithetic=False):
        '''
        返回一个大小为size的样本，验证结果为[0/1]
        :param size: sample size
        :param antithetic: bool
        :return:
        '''
        _, results = self._get_checker().check_and_export(size, antithetic=antithetic)
        return map(lambda result: [0, 1][result], results)

    def _get_rearrange_path_cnt(self):
        pass

    def _get_sample_cnt(self):
        return 100

    def _showRelativeIndex(self):
        '''
        展示使用对偶路径和不使用对偶路径的样本内部相关系数的分布
        :return:
        '''
        checker = self._get_checker()
        sample_cnt = self._get_sample_cnt()
        sample_size = self._get_sample_size()
        samples = [self._get_sample(sample_size) for _ in range(sample_cnt)]
        #  rearrange
        paths, results = checker.check_and_export(self._get_rearrange_path_cnt())
        checker.rearrange(paths, results)
        anti_samples = [self._get_sample(sample_size, antithetic=True) for _ in range(sample_cnt)]
        indexs = [rel_index(sample[0::2], sample[1::2]) for sample in samples]
        anti_indexs = [rel_index(anti_sample[0::2], anti_sample[1::2]) for anti_sample in anti_samples]
        plt.subplot(121)
        plt.hist(indexs, 10)
        plt.subplot(122)
        plt.hist(anti_indexs, 10)
        plt.show()

    def _get_variance_cnt(self):
        '''
        返回统计估计值方差的次数
        :return:
        '''
        return 100

    def _get_variance_size(self):
        '''
        返回为了求估计值的方差需要进行的模型检验的次数
        :return:
        '''
        return 10

    def _showVariance(self):
        '''
        展示使用对偶路径和不使用对偶路径的样本的方差（而非样本方差）的分布
        :return:
        '''
        variance_cnt = self._get_variance_cnt()
        variance_size = self._get_variance_size()
        sample_size = self._get_sample_size()
        variances = []
        for _ in range(variance_cnt):
            samples = [self._get_sample(sample_size) for _ in range(variance_size)]
            check_results = map(lambda sample: sum(sample) / float(len(sample)), samples)
            variances.append(variance(check_results))

        checker = self._get_checker()
        paths, results = checker.check_and_export(self._get_rearrange_path_cnt())
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