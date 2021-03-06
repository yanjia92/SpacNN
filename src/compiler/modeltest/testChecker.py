# -*- coding: utf-8 -*-
from math import fabs

from checker.Checker import Checker
from model.ModelFactory import ModelFactory
from config.SPSConfig import SPSConfig
from module.Module import Constant 


# 测试构建的模型和解析的模型在checker运行的结果一致

THICKNESS = "SCREEN_THICKNESS"
DURATION = 365 * 2
ltl = ['U[1, {}]'.format(int(DURATION)), 'T', 'failure']  # 一年之内系统失效


def get_built_model():
    return ModelFactory().get_built()


def get_parsed_model():
    return ModelFactory.get_parsed()


def get_checker(model, _ltl, duration):
    return Checker(model, _ltl, duration=duration)


def check():
    config = SPSConfig()
    built = get_built_model()
    parsed = get_parsed_model()
    rslt1 = []
    rslt2 = []
    thickness = range(1,10,4)
    for t in thickness:
        config.setParam(THICKNESS, Constant(THICKNESS, t))
        parsed.setConstant(THICKNESS, t)
        checker1 = get_checker(built, ltl, DURATION)
        checker2 = get_checker(parsed, ltl, DURATION)
        rslt1.append(checker1.run())
        rslt2.append(checker2.run())

    precision = 2e-2
    for v1, v2 in zip(rslt1, rslt2):
        assert fabs(v1 - v2) < precision, "v1:{}, v2:{}".format(v1, v2)


if __name__ == "__main__":
    check()

