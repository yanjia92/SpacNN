# -*- coding:utf-8 -*-

from scipy.optimize import leastsq
import numpy as np
from random import random
from math import fabs


def func(param, x):
    k, b = param
    return k * x + b


def linegenerator(param):
    k, b = param

    def wrapper(x):
        return k * x + b
    return wrapper


def error(param, x, y):
    return func(param, x) - y


# 要拟合的参数的初始值
initparam = np.array([1, 1])


def fit(x, y):
    '''
    训练线性模型，计算使得误差最小的k and b
    :param x: list of xs
    :param y: list of ys
    :return: k, b
    '''
    xs = np.array(x)
    ys = np.array(y)
    param = leastsq(error, initparam, args=(xs, ys))
    return param[0]


def _standdiv(xs, ys, func):
    '''
    计算xs, ys所代表的点到由func所代表的直线的平均距离
    :param xs: 点的横坐标数组
    :param ys: 点的纵坐标数组
    :param func: 直线的方程，接受一个x（标量）作为参数，返回y
    :return: 点到直线的平均距离
    '''
    if len(xs) == len(ys) and len(xs) > 0 and func:
        n = len(xs)
        return sum([fabs(func(x) - y) for x, y in zip(xs, ys)]) / n


def main():
    k = 2
    b = 2
    param = tuple([k, b])
    xs = range(10)
    errors = [random() / 10.0 * [-1, 1][random() > 0.5] for _ in xs]
    ys = [func(param, x) + _error for x, _error in zip(xs, errors)]
    minparam = fit(xs, ys)
    print "平均距离：{}".format(_standdiv(xs, ys, linegenerator(minparam)))


if __name__ == "__main__":
    main()
