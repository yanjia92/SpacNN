#-*- coding:utf-8 -*-
from model.ModelFactory import ModelFactory
from checker.Checker import Checker
import logging
from PathHelper import get_sep, get_log_dir


DURATION = 1*365*2


def get_logger():
    logger = logging.getLogger("testCheckingAlgo logging")
    logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "testCheckingAlgo.log", "w"))
    logger.setLevel(logging.INFO)
    return logger


def get_checker():
    built = ModelFactory.get_built()
    ltl = ["U[1, {}]".format(int(DURATION)), "T", "failure"]
    checker = Checker(model=built, ltl=ltl, duration=DURATION, c=0.7, d=0.01)
    return checker


def t1():
    '''测试生成的随机路径要么长度达到最长(duration)，要么包含failure ap'''
    checker = get_checker()
    PATH_CNT = 3000
    logger = get_logger()
    for _ in range(PATH_CNT):
        result, path = checker.gen_random_path()
        verified = checker.verify(path)
        if not verified and len(path) != DURATION:
            logger.info("path:{}".format(str(path)))


def t2():
    '''测试built模型运行checker的结果与PRISM中运行的一致'''
    checker = get_checker()
    thickness = range(1, 6)
    probs = []
    for t in thickness:
        ModelFactory.setParam("SCREEN_THICKNESS", t)
        probs.append(checker.run())
    print probs

if __name__ == "__main__":
    t2()


