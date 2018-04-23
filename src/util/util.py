# -*- coding:utf-8 -*-
from math import *

def sigmond(x):
    return map(lambda _x: 1.0/(1.0 + exp(-_x)), x)

def sigmond_prime(x):
    # 返回sigmond函数的导数
    v1 = sigmond(x)
    return map(lambda _x: _x*(1 - _x), v1)


def interval(a, b, step):
    # 返回[a,b]之间的一系列数值组成的数组,数组之间的step为step
    result = []
    result.append(a)
    while a <= b:
        result.append(a)
        a += step
    return result