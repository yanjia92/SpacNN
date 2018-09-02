# -*- coding: utf-8 -*-
from math import *
import random
from scipy.optimize import leastsq
import numpy as np
from math import pow
from math import e


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


def expo_pdf(x, lamda):
    '''
    指数分布的概率密度函数
    :param x: x
    :param lamda: parameter lambda
    :return: pdf_lambda(x)
    '''
    if x <= 0:
        return 0
    return lamda * pow(e, -lamda * x)


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


def uniform(a, b, samples=1):
    '''
    产生介于a,b之间的服从均匀分布的随机数
    :param a:
    :param b:
    :param samples: 所需的随机样本数
    :return: 随机样本 type list
    '''
    randoms = []
    if a < b and samples > 0:
        for _ in range(samples):
            randoms.append(a + (b - a) * random.random())
        return randoms
    else:
        return []


def standDiv(xs, ys):
    '''
    计算二维坐标点距离通过最小二乘法拟合出的曲线的平均距离
    :param xs: list of pointer's x
    :param ys: list of pointer's y
    :return: 点到拟合出的直线的距离的平均值
    '''
    if not (len(xs) == len(ys) and len(xs) > 0):
        return

    def error(param, x, y):
        return func(param, x) - y

    def func(param, x):
        k, b = param
        return k * x + b

    xs = np.array(xs)
    ys = np.array(ys)
    initparam = np.array([1, 1])
    param = leastsq(error, initparam, args=(xs, ys))
    param = param[0]

    def linegenerator(param):
        def wrapper(x):
            k, b = param
            return k * x + b
        return wrapper

    linefunc = linegenerator(param)
    return sum([fabs(linefunc(x) - y) for x, y in zip(xs, ys)]) / float(len(xs))



class ErrorType():
    SQ_DIFF = 0
