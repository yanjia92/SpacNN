# -*- coding: utf-8 -*-
from util.MathUtils import pcf
from math import log
import matplotlib.pyplot as plt

# rewrite the solar battery into a CTMC model
def rewrite():
    k = 0.0039
    thickness = 35
    doses = map(lambda day: day/365.0* k* thickness, range(1, 1000))
    # 电池输出功率与NIEL剂量之间的关系
    # 其中a服从一个正态分布
    a_mu = 0.1754 # expectation of a
    a_sigma = 0.02319029 # 标准差
    b = 12.142
    P_threshold= 0.8
    xs = map(lambda dose: (1 - P_threshold)/log(1 + dose * b), doses)
    std_xs = map(lambda x: (x-a_mu)/a_sigma, xs)
    probs = map(lambda x: 1 - pcf(x), std_xs)
    rates = map(lambda p: p/(1-p), probs)
    plt.plot(range(1, 1000), probs) # 失效概率与天数的关系曲线
    plt.plot(range(1, 1000), rates) # 失效速率与天数的关系曲线
    plt.show()

if __name__ == "__main__":
    rewrite()
