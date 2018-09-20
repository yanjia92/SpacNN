# -*- coding:utf-8 -*-
from unittest import TestCase
from random import random
from math import sqrt


# 验证对于离散分布（0-1分布）来说，对偶变量可以有效减小估计值方差


class AntitheticMapper(object):
    def __init__(self):
        self._max_map_cnt = 250
        self._map_cnt = 0

    def map(self, num):
        if self._map_cnt >= self._max_map_cnt:
            return random()
        self._map_cnt += 1
        if num < 0 or num >= 1:
            return
        return 1 - num


class VarReductionTest(TestCase):
    def setUp(self, debug=True):
        self._sample_cnt = 100 # 样本个数
        self._sample_size = 30 # 每个样本的取样的个数
        self._p = random() # 0-1分布的参数p
        self._generator = random # 随机数的生成器

    def _get_sample(self, antithetic=False):
        if antithetic:
            mapper = AntitheticMapper()
            sample = [self._generator() for _ in range(self._sample_size / 2)]
            anti_sample = map(mapper.map, sample)
            sample.extend(anti_sample)
            return sample
        if self._sample_size <= 0:
            return []
        return [self._generator() for _ in range(self._sample_size)]

    def _compute_var(self, nums):
        if not nums or not len(nums):
            return
        average = sum(nums) / len(nums)
        return sum([(num - average) ** 2 for num in nums]) / len(nums)

    def testComputeVars(self):
        '''
        计算100个样本的方差
        :return: 使用普通抽样对偶抽样的方差的平均值
        '''
        predictions = []
        anti_predictions = []
        for _ in range(self._sample_cnt):
            sample = self._get_sample()
            anti_sample = self._get_sample(antithetic=True)
            sample = [[0, 1][num > self._p] for num in sample]
            anti_sample = [[0, 1][anti_num > self._p] for anti_num in anti_sample]
            predictions.append(float(sum(sample)) / len(sample))
            anti_predictions.append(float(sum(anti_sample)) / len(anti_sample))
        variance = self._compute_var(predictions)
        anti_variance = self._compute_var(anti_predictions)
        return variance, anti_variance

    def testVarReduction(self):
        variances = [self.testComputeVars() for _ in range(100)]
        anti_variances = [t[1] for t in variances]
        variances = [t[0] for t in variances]
        print sum(variances) / len(variances)
        print sum(anti_variances) / len(anti_variances)

    def cov(self, nums1, nums2):
        exy = sum([x*y for x,y in zip(nums1, nums2)]) / float(len(nums1))
        ex = sum(nums1) / float(len(nums1))
        ey = sum(nums2) / float(len(nums2))
        return exy - ex * ey

    def rel_index(self, nums1, nums2):
        cov = self.cov(nums1, nums2)
        std1 = sqrt(self.cov(nums1, nums1))
        std2 = sqrt(self.cov(nums2, nums2))
        return cov / (std1 * std2)

    def testRelIndex(self):
        nums1 = [1, -1, -1, 1, -1, -1, -1, 1, -1, -1]
        nums2 = [-1, 1,  1, 1, -1, -1, -1, 1, -1, -1]
        print self.rel_index(nums1, nums2)