# -*- coding:utf-8 -*-
import numpy as np

def sigmond(x):
    return 1.0/(1.0 + np.exp(-x))

def sigmond_prime(x):
    # 返回sigmond函数的导数
    return sigmond(x)*(1-sigmond(x))

def interval(a, b, step):
    # 返回[a,b]之间的一系列数值组成的数组,数组之间的step为step
    result = []
    result.append(a)
    while a <= b:
        a += step
        result.append(a)
    return result