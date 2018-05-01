# -*- coding: utf-8 -*-

# 验证思路
#   1. 对day变量随机取n(maybe 10?)个值，对每个模型的失效概率进行记日志，和PRISM中的stimulate结果进行对比，观察是否相同。


import logging 
from PathHelper import get_log_dir, get_sep
from model.ModelFactory import ModelFactory

logger = logging.getLogger("test model same logging")
logPath = get_log_dir() + get_sep() + "testmodelsame.log"
logger.addHandler(logging.FileHandler(logPath))
logger.setLevel(logging.INFO)

def test():
    built = ModelFactory.get_built()
    day_vals = range(1, 311, 50)
    logger.info("day_vals = {}".format(day_vals))
    sb_module = built.getModuleByName("SB")
    sb_fail_cmd = sb_module.getCommand("sb_fail_cmd")
    s3r_module = built.getModuleByName("S3R")
    s3r_fail_cmd = s3r_module.getCommand("s3r_fail_cmd")
    for day_val in day_vals:
        built.setVariable("day", day_val)
        sb_fail_prob = sb_fail_cmd.prob()/4.0
        s3r_fail_prob = s3r_fail_cmd.prob()/4.0
        logger.info("day={}".format(day_val) + ", sb_fail_prob=" + format(sb_fail_prob, '.15e'))
        logger.info("day={}".format(day_val) + ", s3r_fail_prob=" + format(s3r_fail_prob, '.15e'))


if __name__ == "__main__":
    test()

