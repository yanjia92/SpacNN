# -*- coding: utf-8 -*-
from module.Module import *
from util.MathUtils import *
from util.util import *
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
import unittest

YEAR=5

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
            for v in [Variable("day", i) for i in interval(1, 365*YEAR, 1)]:
                dose = v.getValue() / 365.0 * (s3r.getConstant("S3R_K").getValue() /
                                               self.config.getParam("SCREEN_THICKNESS").getValue())
                x = s3r.getConstant("S3R_DELTAV_THRESHOLD").getValue() / (
                s3r.getConstant("S3R_B").getValue() * exp(s3r.getConstant("S3R_B").getValue() * dose))
                std_x = (x - s3r.getConstant("S3R_A_MU").getValue()) / s3r.getConstant("S3R_A_SIGMA").getValue()
                p = 1 - pcf(std_x)
                ps.append(p)
            if t == 4:
                print t
                print ps[-5:]



if __name__ == '__main__':
    unittest.main()
