# -*- coding: utf-8 -*-
from math import fabs
from model.ModelFactory import ModelFactory
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
from compiler.PRISMParser import ModelConstructor
from checker.Checker import Checker

# 测试构建的模型和解析的模型在checker运行的结果一致

THICKNESS = "SCREEN_THICKNESS"


def get_built_model():
    config = SPSConfig()
    return ModelFactory(ModuleFactory(config)).spsmodel()


def get_parsed_model():
    file_path = "../../../prism_model/smalltest.prism"
    return ModelConstructor().parseModelFile(file_path)


def get_checker(model, ltl):
    return Checker(model, ltl)


def check():
    built = get_built_model()
    parsed = get_parsed_model()

    rslt1 = []
    rslt2 = []
    thickness = range(1, 10)
    ltl = ['U[1, {0}]'.format(365*5*2), 'T', 'failure']  # 三年之内系统失效
    for t in thickness:
        built.setConstant(THICKNESS, t)
        parsed.setConstant(THICKNESS, t)
        checker1 = get_checker(built, ltl)
        checker2 = get_checker(parsed, ltl)
        rslt1.append(checker1.run())
        rslt2.append(checker2.run())

    precision = 1e-4
    for v1, v2 in zip(rslt1, rslt2):
        assert fabs(v1 - v2) < precision, "v1:{}, v2:{}".format(v1, v2)


if __name__ == "__main__":
    check()