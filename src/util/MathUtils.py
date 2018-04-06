# -*- coding: utf-8 -*-
from math import *
# generate random variable from a exponential distribution
# given that it's less than t.
# e.g. implementation of forcing.
# if forcing is False, return normal random variable from the exponential distribution
# of the rate parameter set to be lamda.
def randomExpo(lamda, t=None, forcing=True):
    import random, math
    rnd = random.uniform(0, 1)
    if forcing and t:
        return math.log(1-rnd*(1-math.exp(-1*lamda*t)))/(-1*lamda)
    else:
        return math.log(1-rnd)/(-1*lamda)


# 计算标准正态分布的累积分布函数
def pcf(x):
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1
    if x < 0:
        sign = -1
    x = fabs(x) / sqrt(2.0)

    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * exp(-x * x)

    return 0.5 * (1.0 + sign * y)