# -*- coding: utf-8 -*-

import unittest
from PathHelper import *
from compiler.PRISMParser import ModelConstructor
from checker.Checker import Checker
from compiler.LTLParser import LTLParser
import logging
from module.ModulesFile import ModelType
from module.Module import Constant

logger = logging.getLogger("syncunittest_logging")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "paths.log"))


class DTMCSyncUnittest(unittest.TestCase):

    def setUp(self):
        filepath = get_prism_model_dir() + get_sep() + "smalltest.prism"
        self.model_constructor = ModelConstructor()
        self.model = self.model_constructor._parse(filepath)
        self.duration = 180
        self.model.duration = self.duration
        ltl = "true U<={} failure".format(self.duration)
        parsed = LTLParser().build_parser().parse_line(ltl)
        self.checker = Checker(model=self.model, ltl=parsed)

    def test_parsing(self):
        self.assertEqual(self.model.model_type, ModelType.DTMC)

    def test_gen_path(self):
        # 测试生成路径的正确性
        # 生成的路径要么总长为duration,要么出现failure
        for _ in range(5000):
            path = self.model.get_random_path_V2()
            for step in path:
                logger.info(step)
            logger.info("----------------")
            if {"failure"} in [step.ap_set for step in path]:
                continue
            passed_time = path[-1].next_move.passed_time + \
                path[-1].next_move.holding_time
            if int(passed_time) < self.duration:
                for step in path:
                    logger.error(step)
                logger.error("-------------")

    def test_checking(self):
        thickness_vals = range(1, 10, 1)
        constant_objs = [Constant("SCREEN_THICKNESS", v)
                         for v in thickness_vals]
        for obj in constant_objs:
            self.model_constructor._parser.vcf_map[obj.get_name()].set_value(
                obj.get_value())
            self.model.commPrepared = False
            logger.info(
                "param={}, checker's result={}".format(
                    obj.get_value(),
                    self.checker.run_checker()))
