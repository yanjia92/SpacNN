#-*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from checker.Checker import Checker
import logging
from PathHelper import get_sep, get_log_dir

def get_logger():
    logger = logging.getLogger("testCheckingAlgo logging")
    logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "testCheckingAlgo.log", "w"))
    logger.setLevel(logging.INFO)
    return logger


def t1():
    '''测试生成的随机路径要么长度达到最长(duration)，要么包含failure ap'''
    built = ModelFactory.get_built()
    DURATION = 1*365*2
    ltl = ["U[1, {}]".format(int(DURATION)), "T", "failure"]
    checker = Checker(model=built, ltl=ltl, duration=DURATION)
    PATH_CNT = 3000
    logger = get_logger()
    for _ in range(PATH_CNT):
        result, path = checker.gen_random_path()
        verified = checker.verify(path)
        if not verified and len(path) != DURATION:
            logger.info("path:{}".format(str(path)))


if __name__ == "__main__":
    t1()


