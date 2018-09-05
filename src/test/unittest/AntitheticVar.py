# -*- coding:utf-8 -*-
from unittest import TestCase
from random import random


class Test(TestCase):
    def testAntitheticVarReduction(self):
        '''
        验证对偶变量能够减小估计值方差
        '''
        sample = 100
        estimate_sample = 100
        estimates = []
        for _ in range(sample):
            estimate = sum([random() for _ in range(estimate_sample)]) / estimate_sample
            estimates.append(estimate)
        average = sum(estimates) / sample
        variance = sum([(estimate - average) ** 2 for estimate in estimates]) / sample

        anti_estimates = []
        for _ in range(sample):
            rnds = [random() for _ in range(estimate_sample/2)]
            anti_rnds = map(lambda rnd: 1 - rnd, rnds)
            rnds.extend(anti_rnds)
            estimate = sum(rnds) / estimate_sample
            estimates.append(estimate)
        anti_average = sum(anti_estimates) / sample
        anti_variance = sum([(anti_estimate - anti_average) ** 2 for anti_estimate in anti_estimates]) / sample

        print variance
        print anti_variance

