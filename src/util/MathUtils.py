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
        return log(1-rnd*(1-math.exp(-1*lamda*t)))/(-1*lamda)
    else:
        return log(1-rnd)/(-1*lamda)


# const double a1 =  0.254829592;
# const double a2 = -0.284496736;
# const double a3 =  1.421413741;
# const double a4 = -1.453152027;
# const double a5 =  1.061405429;
# const double p  =  0.3275911;
# formula s3r_sign = s3r_std_cdf_x < 0 ? -1 : 1;
# formula s3r_std_cdf_x_2 = s3r_sign * s3r_std_cdf_x / pow(2.0, 0.5);
# formula s3r_t = 1.0/(1.0 + p * s3r_std_cdf_x_2);
# formula s3r_y = 1.0 - (((((a5*s3r_t + a4)*s3r_t) + a3)*s3r_t + a2)*s3r_t + a1)*s3r_t*pow(e, -s3r_std_cdf_x_2 * s3r_std_cdf_x_2);
# formula s3r_fail_prob = 1 - 0.5 * (1.0 + s3r_sign * s3r_y);  // 根据s3r所受电离能损剂量计算出的失效概率


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

class ErrorType():
    SQ_DIFF = 0
