# -*- coding: utf-8 -*-
import logging
import unittest
from math import fabs

from compiler.PRISMParser import ModelConstructor
from config.SPSConfig import SPSConfig
from model.ModuleFactory import ModuleFactory
from module.Module import *
from util.MathUtils import *
from util.util import *

logger = logging.getLogger("s3r test logger")
logger.addHandler(logging.FileHandler("../log/tests3r.log", "w"))
logger.setLevel(logging.INFO)


YEAR = 5


class TestCase(unittest.TestCase):
    def setUp(self):
        self.config = SPSConfig()
        self.modulefactory = ModuleFactory(self.config)

    def tests3rfail(self):
        results = []
        s3r = self.modulefactory.s3rmodule()
        logger.info("===============built===============")
        for t in range(4, 5):
            self.config.setParam("SCREEN_THICKNESS", t)
            ps = []
            xs = []
            std_xs = []
            for v in [Variable("day", i) for i in interval(1, 365*YEAR, 1)]:
                dose = v.get_value() / 365.0 * (s3r.getConstant("S3R_K").get_value() /
                                                self.config.getParam("SCREEN_THICKNESS").get_value())
                # 阈值电压漂移
                xs.append(dose)
                x = s3r.getConstant("S3R_DELTAV_THRESHOLD").get_value() / (
                    s3r.getConstant("S3R_B").get_value() * exp(s3r.getConstant("S3R_B").get_value() * dose))
                std_x = (x - s3r.getConstant("S3R_A_MU").get_value()) / s3r.getConstant("S3R_A_SIGMA").get_value()
                p = 1 - pcf(std_x)
                ps.append(p)
                std_xs.append(std_x)
            logger.info("thickness={}, p_max={}".format(t, ps[-1]))
            results.append(ps)

        return results

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
        for thickness in range(4, 5):
            probs = []
            parsed.setConstant("SCREEN_THICKNESS", thickness)
            for d in days:
                parsed.setVariable("day", d)
                fail_prob = s3r_mdl.commands["s3r_fail_cmd"].prob()
                probs.append(fail_prob)
            results.append(probs)
            logger.info("thickness={}, p_max={}".format(thickness, probs[-1]))
        return results

    def test_final(self):
        results_built = self.tests3rfail()[0]
        results_parsed = self.testparsing()[0]
        assert len(results_built) == len(results_parsed), "results array length not equal. "
        precision = 1e-6
        for index, (v1, v2) in enumerate(zip(results_parsed, results_built)):
            assert fabs(v1 - v2) <= precision, "day={}, v1={}, v2={}".format(index+1, v1, v2)

if __name__ == '__main__':
    unittest.main()
