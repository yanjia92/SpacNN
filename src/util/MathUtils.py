# -*- coding: utf-8 -*-
from math import *
import random

# generate random variable from a exponential distribution
# given that it's less than t.
# e.g. implementation of forcing.
# if forcing is False, return normal random variable from the exponential distribution
# of the rate parameter set to be lambda.
def randomExpo(lamda, t=None, forcing=True):
    rnd = random.uniform(0, 1)
    if forcing and t:
        return log(1-rnd*(1-exp(-1*lamda*t)))/(-1*lamda)
    else:
        return log(1-rnd)/(-1*lamda)


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


def powe(x):
    return pow(e, x)


def rand(a, b):
    return (b - a) * random.random() + a


def make_matrix(m, n, fill=0.0):
    mat = []
    for i in range(m):
        mat.append([fill] * n)
    return mat


def sigmoid(x):
    return 1.0 / (1.0 + exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


def format_float(v, n):
    '''
    将浮点数v保留n位小数
    :param v: float
    :param n: int
    :return:
    '''
    if not isinstance(n, int) or n < 0:
        return None
    str_v = str(v)
    is_float = isinstance(v, float)
    if not is_float:
        str_v += "."
        str_v += "0" * n
        return float(str_v)
    else:
        int_part, float_part = str_v.split(".")
        while len(float_part) < n:
            float_part += "0"
        float_part = float_part[:n]
        return float(int_part + "." + float_part)


class ErrorType():
    SQ_DIFF = 0
