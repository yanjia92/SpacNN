# -*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from checker.Checker import Checker
import logging
from PathHelper import get_sep, get_log_dir, get_prism_model_dir
from util.CsvFileHelper import parse_csv
from math import fabs
import random


DURATION = 1*365*2
c = 0.6
d = 0.02
# d = 0.3


def get_prism_checking_result():
    filepath = get_prism_model_dir() + get_sep() + "YEAR1_T_1_5_1"
    return parse_csv(filepath)


def get_logger():
    logger = logging.getLogger("testCheckingAlgo logging")
    logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "testCheckingAlgo.log", "w"))
    logger.setLevel(logging.INFO)
    return logger


def get_checker(model):
    # built = ModelFactory.get_built()
    ltl = ["U[1, {}]".format(int(DURATION)), "T", "failure"]
    checker = Checker(model=model, ltl=ltl, duration=DURATION, c=c, d=d)
    return checker


def t1():
    '''测试生成的随机路径要么长度达到最长(duration)，要么包含failure ap'''
    checker = get_checker(ModelFactory.get_parsed())
    checker.model.duration = DURATION
    PATH_CNT = 3000
    logger = get_logger()
    logger.setLevel(logging.ERROR)
    for _ in range(PATH_CNT):
        result, path = checker.gen_random_path()
        if len(path) < DURATION-1:
            logger.info("Failed path found.")
        verified = checker.verify(path)
        if verified is False and len(path) != DURATION:
            logger.error("path:{}".format(str(path)))
            logger.error("path'len={}".format(len(path)))


def t2():
    '''测试built模型运行checker的结果与PRISM中运行的一致'''
    prism_result_x, prism_result_y = get_prism_checking_result()  # (1, 5, 1)
    checker = get_checker(ModelFactory.get_built())
    samplesize = checker.get_sample_size()
    thickness = range(1, 6)
    probs = []
    logger = get_logger()
    for t in thickness:
        ModelFactory.setParam("SCREEN_THICKNESS", t)
        checker.model.prepareCommands()
        probs.append(checker.run())
    logger.info("samples={},c={},d={}".format(samplesize, c, d))
    logger.info(probs)
    for v1, v2 in zip(probs, prism_result_y[-(len(probs)):]):
        logger.info("diff={}".format(fabs(v1 - v2)))


def set_param(name, value):
    '''用于对parsed model进行参数设置'''
    ModelFactory.model_constructor.parser.vcf_map[name].value = value


def t3():
    '''测试parsed模型运行checker的结果与PRISM中运行的一致'''
    logger = get_logger()
    prism_result_x, prism_result_y = get_prism_checking_result()  # (1, 5, 1)
    checker = get_checker(ModelFactory.get_parsed())
    samplesize = checker.get_sample_size()
    logger.info("Sampling size = {}".format(samplesize))
    thickness = range(1, 2)
    probs = []
    checker.model.prepareCommands()
    for t in thickness:
        # ModelFactory.setParam("SCREEN_THICKNESS", t)
        set_param("SCREEN_THICKNESS", t)
        # checker.model.setConstant("SCREEN_THICKNESS", t)
        probs.append(checker.run())
    logger.info("samples={},c={},d={}".format(samplesize, c, d))
    logger.info(probs)
    for v1, v2 in zip(probs, prism_result_y[:len(probs)]):
        logger.info("Diff = %.2f%%" % fabs((v1-v2)/v2*100))

if __name__ == "__main__":
    t1()
    # t2()
    # t3()

