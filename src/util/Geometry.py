# -*- coding: utf-8 -*-
from math import *
import numpy as np
from scipy.optimize import leastsq


def aver_distance(xs, ys):
    '''
    返回这些点到最小二乘法拟合出的直线的平均距离
    :param xs:
    :param ys:
    :return:
    '''
    line_func = generate_line_func(xs, ys)
    distances = []
    for x, y in zip(xs, ys):
        distances.append(point_2_line(x, y, line_func))
    return sum(distances) / len(distances)


def signed_distance(xs, ys):
    line_func = generate_line_func(xs, ys)
    return _signed_distance(xs, ys, line_func)


def _signed_distance(xs, ys, line_func):
    '''
    计算点到直线的signed距离之和
    :param xs:
    :param ys:
    :param line_func:
    :return:
    '''
    distance = 0.0
    for x, y in zip(xs, ys):
        sign = 1.0
        if line_func(x) > y:
            sign = -1
        distance += (sign * point_2_line(x, y, line_func))
    return distance


def generate_line_func(xs, ys):
    '''
    根据最小二乘法拟合出一条直线并返回直线方程
    :param xs:
    :param ys:
    :return: function of form: y = k*x+b
    '''
    def func(param, x):
        k, b = param
        return k * x + b

    def error(param, x, y):
        return func(param, x) - y

    xs = np.array(xs)
    ys = np.array(ys)
    init_param = np.array([1, 1])
    param = leastsq(error, init_param, args=(xs, ys))
    param = param[0]

    def linegenerator(param):
        def wrapper(x):
            k, b = param
            return k * x + b
        return wrapper

    return linegenerator(param)


def point_2_line(x, y, line_func):
    '''
    计算点到直线的垂直距离
    公式：dist = fabs((ax+by+c) / sqrt(a^2+b^2))
    :param x:
    :param y:
    :param line_func: function that is of form: y = ax + b
    :return:
    '''
    b = -1
    a = line_func(1) - line_func(0)
    c = line_func(0)
    return fabs((a*x+b*y+c) / sqrt(a**2+b**2))