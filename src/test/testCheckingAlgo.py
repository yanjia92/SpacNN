# -*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from checker.Checker import Checker
import logging
from PathHelper import get_sep, get_log_dir, get_prism_model_dir
from util.CsvFileHelper import parse_csv
from math import fabs
import random


DURATION = 1*365*2
c = 0.4
d = 0.01


def get_prism_checking_result():
    filepath = get_prism_model_dir() + get_sep() + "YEAR1_T_1_5_1"
    return parse_csv(filepath)


def get_logger():
    logger = logging.getLogger("testCheckingAlgo logging")
    logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "testCheckingAlgo.log", "a"))
    logger.setLevel(logging.INFO)
    return logger


def get_checker():
    built = ModelFactory.get_built()
    ltl = ["U[1, {}]".format(int(DURATION)), "T", "failure"]
    checker = Checker(model=built, ltl=ltl, duration=DURATION, c=c, d=d)
    return checker


def t1():
    '''测试生成的随机路径要么长度达到最长(duration)，要么包含failure ap'''
    checker = get_checker()
    PATH_CNT = 3000
    logger = get_logger()
    logger.setLevel(logging.ERROR)
    for _ in range(PATH_CNT):
        result, path = checker.gen_random_path()
        if len(path) < DURATION:
            logger.info("Failed path found.")
        verified = checker.verify(path)
        if not verified and len(path) != DURATION:
            logger.error("path:{}".format(str(path)))


def t2():
    '''测试built模型运行checker的结果与PRISM中运行的一致'''
    prism_result_x, prism_result_y = get_prism_checking_result()  # (1, 5, 1)
    checker = get_checker()
    samplesize = checker.get_sample_size()
    thickness = range(5, 6)
    probs = []
    logger = get_logger()
    for t in thickness:
        ModelFactory.setParam("SCREEN_THICKNESS", t)
        probs.append(checker.run())
    logger.info("samples={},c={},d={}".format(samplesize, c, d))
    logger.info(probs)
    for v1, v2 in zip(probs, prism_result_y[-(len(probs)):]):
        logger.info("diff={}".format(fabs(v1 - v2)))


if __name__ == "__main__":
    # t1()
    t2()

