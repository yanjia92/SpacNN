# -*- coding: utf-8 -*-
from module.Module import *
from util.MathUtils import *
from util.util import *
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
import unittest
from compiler.PRISMParser import ModelConstructor

import logging

logger = logging.getLogger("s3r test logger")
logger.addHandler(logging.FileHandler("../log/tests3r.log", "w"))
logger.setLevel(logging.INFO)


YEAR = 5


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = SPSConfig()
        self.modulefactory = ModuleFactory(self.config)

    def tests3rfail(self):
        timer = self.modulefactory.timermodule()
        s3r = self.modulefactory.s3rmodule()
        ps = []
        logger.info("===============built===============")
        for t in range(1, 11):
            self.config.setParam("SCREEN_THICKNESS", t)
            xs = []
            std_xs = []
            for v in [Variable("day", i) for i in interval(1, 365*YEAR, 1)]:
                dose = v.getValue() / 365.0 * (s3r.getConstant("S3R_K").getValue() /
                                               self.config.getParam("SCREEN_THICKNESS").getValue())
                # 阈值电压漂移
                xs.append(dose)
                x = s3r.getConstant("S3R_DELTAV_THRESHOLD").getValue() / (
                s3r.getConstant("S3R_B").getValue() * exp(s3r.getConstant("S3R_B").getValue() * dose))
                std_x = (x - s3r.getConstant("S3R_A_MU").getValue()) / s3r.getConstant("S3R_A_SIGMA").getValue()
                p = 1 - pcf(std_x)
                ps.append(p)
                std_xs.append(std_x)
            logger.info("thickness={}, p_max={}".format(t, ps[-1]))

    def get_parsed(self):
        constructor = ModelConstructor()
        model = constructor.parseModelFile("../../prism_model/smalltest.prism")
        return model

    # 测试同样的数据for parsed model
    def testparsing(self):
        parsed = self.get_parsed()
        days = range(1, YEAR * 365 + 1)
        s3r_mdl = parsed.getModuleByName("S3R")
        results = []
        logger.info("===============parsed===============")
        for thickness in range(1, 11):
            probs = []
            parsed.setConstant("SCREEN_THICKNESS", thickness)
            for d in days:
                parsed.setVariable("day", d)
                fail_prob = s3r_mdl.commands["s3r_fail_cmd"].prob()
                probs.append(fail_prob)
            results.append(probs)
            logger.info("thickness={}, p_max={}".format(thickness, probs[-1]))
        return results


if __name__ == '__main__':
    unittest.main()
