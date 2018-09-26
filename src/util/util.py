# -*- coding:utf-8 -*-
from math import *


def sigmond(x):
    return map(lambda _x: 1.0/(1.0 + exp(-_x)), x)


def sigmond_prime(x):
    # 返回sigmond函数的导数
    v1 = sigmond(x)
    return map(lambda _x: _x*(1 - _x), v1)


def interval(a, b, step):
    '''
    return a list of data specified by start(a), end(b), and step
    :param a: start
    :param b: end
    :param step: step
    :return: [data]
    '''
    result = []
    if a > b or step < 0:
        return []
    if a == b and step == 0:
        result.append(a)
        return result
    while a <= b:
        result.append(a)
        a += step
    return result

