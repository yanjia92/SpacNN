import logging
import unittest
logger = logging.getLogger('test fail prob log')
logger.addHandler(logging.FileHandler('../log/testfailprob.log'))
logger.setLevel(logging.INFO)
from config.SPSConfig import SPSConfig
from model.ModuleFactory import ModuleFactory
from module.Module import *
from util.util import *
from util.MathUtils import *
from math import log


class Test(unittest.TestCase):
    def setUp(self):
        self.config = SPSConfig()
        self.factory = ModuleFactory(self.config)

    def testsbfail(self):
        module = self.factory.sbmodule()
        config = self.config

        def f(day_var):
            def inner():
                day = day_var.get_value()
                dose = module.getConstant(
                    'SB_K') * config.getParam('SCREEN_THICKNESS') * day / 365.0
                x = (-module.getConstant('SB_P_THRESHOLD') + 1) / \
                    (log(module.getConstant('SB_B') * dose + 1))
                std_x = 1.0 / (module.getConstant('SB_A_SIGMA') /
                               (-module.getConstant('SB_A_MU') + x))
                return 1 - pcf(std_x)
            return inner
        for varday in [Variable('day', v) for v in interval(1, 365, 1)]:
            ff = f(varday)
            logger.info(
                'sb: day_{0}, prob={1}'.format(
                    varday.get_value(), ff()))

    def tests3rfail(self):
        module = self.factory.s3rmodule()
        config = self.config

        def f(day_var):
            def inner():
                day = day_var.get_value()
                dose = module.getConstant('S3R_K') / config.getParam(
                    'SCREEN_THICKNESS') * (day / 365.0)
                x = config.getParam('S3R_DELTAV_THRESHOLD') / (
                    config.getParam('S3R_B') * pow(e, config.getParam('S3R_B') * dose))
                std_x = (-config.getParam('S3R_A_MU') + x) / \
                    config.getParam('S3R_A_SIGMA').get_value()
                logger.info(
                    's3r: day_{0}, std_x={1}'.format(
                        day_var.get_value(), std_x))
                p = 1 - pcf(std_x)
                return p
            return inner
        for varday in [Variable('day', v) for v in interval(1, 365, 1)]:
            ff = f(varday)
            logger.info(
                's3r: day_{0}, prob={1}'.format(
                    varday.get_value(), ff()))


if __name__ == "__main__":
    unittest.main()
