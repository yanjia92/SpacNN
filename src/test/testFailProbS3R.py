# -*- coding: utf-8 -*-
from module.Module import *
from util.MathUtils import *
from util.util import *
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
import unittest
import numpy as np
import matplotlib.pyplot as plt
import math

import logging

logger = logging.getLogger("s3r test logger")
logger.addHandler(logging.FileHandler("../log/tests3r.log", "a"))
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
        for t in range(1, 11):
            self.config.setParam("SCREEN_THICKNESS", t)
            xs = []
            ys = []
            std_xs = []
            for v in [Variable("day", i) for i in interval(1, 365*YEAR, 1)]:
                dose = v.getValue() / 365.0 * (s3r.getConstant("S3R_K").getValue() /
                                               self.config.getParam("SCREEN_THICKNESS").getValue())
                # 阈值电压漂移
                xs.append(dose)
                mean = s3r.getConstant("S3R_A_MU").getValue()
                sigma = s3r.getConstant("S3R_A_SIGMA").getValue()
                b = s3r.getConstant("S3R_B").getValue()
                deltav = np.random.normal(mean, sigma) * b * math.exp(b * dose)
                ys.append(deltav)
                x = s3r.getConstant("S3R_DELTAV_THRESHOLD").getValue() / (
                s3r.getConstant("S3R_B").getValue() * exp(s3r.getConstant("S3R_B").getValue() * dose))
                std_x = (x - s3r.getConstant("S3R_A_MU").getValue()) / s3r.getConstant("S3R_A_SIGMA").getValue()
                p = 1 - pcf(std_x)
                ps.append(p)
                std_xs.append(std_x)
            # if t == 4:
            #     print ps[0]
            #     print ps[-1]
            #     print "normal prob= %f" % (reduce(lambda x,y: x*y, map(lambda p: 1.0-p, ps)))
            #     plt.xlabel("IEL dose")
            #     plt.ylabel("deltaV")
            #     plt.plot(xs,ys, color="black")
            #     plt.show()
            # print "std_x=%f p=%f" % (std_xs[-1], ps[-1])
            logger.info("thickness=%d, std_x=%f, p=%.7f", t, std_xs[-1], ps[-1])
            if t == 10:
                logger.info("\n")

if __name__ == '__main__':
    unittest.main()
