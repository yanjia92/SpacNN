# -*- coding: utf-8 -*-
from math import *
import random
from scipy.optimize import leastsq
import numpy as np
from math import pow
from math import e


def expo_rnd(lamda):
    '''
    return random number which is distributed under exponential distribution
    :param lamda: rate parameter
    :return: random number
    '''
    rnd = random.uniform(0, 1)
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


def averageDistanceToLine(xs, ys):
    '''
    计算二维坐标点距离通过最小二乘法拟合出的曲线的平均距离
    :param xs: list of pointer's x
    :param ys: list of pointer's y
    :return: 点到拟合出的直线的距离的平均值
    '''
    if not (len(xs) == len(ys) and len(xs) > 0):
        return

    def func(param, x):
        k, b = param
        return k * x + b

    def error(param, x, y):
        return func(param, x) - y

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


def cov(nums1, nums2):
    '''
    协方差
    :param nums1: array of numbers
    :param nums2: array of numbers
    :return: covariance of two arrays
    '''
    exy = sum([x*y for x,y in zip(nums1, nums2)]) / float(len(nums1))
    ex = sum(nums1) / float(len(nums1))
    ey = sum(nums2) / float(len(nums2))
    return exy - ex * ey


def rel_index(nums1, nums2):
    '''
    相关系数
    formula: index = cov(arr1, arr2) / std_var(arr1) * std_var(arr2)
    :param nums1:
    :param nums2:
    :return:
    '''
    c = cov(nums1, nums2)
    std_var1 = sqrt(cov(nums1, nums1))
    std_var2 = sqrt(cov(nums2, nums2))
    return c / (std_var1 * std_var2)


def almost_equal(f1, f2, sig_fig=6):
    '''
    判断两个float近似相等
    近似相等意味着int(f1) == int(f2) and f1和f2小数点后的sig_fig位有效数字相等
    :param f1: float
    :param f2: float
    :param sig_fig: 小数点后的有效数字位数
    :return:
    '''
    if int(f1) != int(f2):
        return False
    f1 -= int(f1)
    f2 -= int(f2)
    return int(f1*(10**sig_fig)) == int(f2*(10**sig_fig))


def variance(nums):
    return cov(nums, nums)


class ErrorType():
    SQ_DIFF = 0
