# -*- coding:utf-8 -*-
import unittest
from compiler.PRISMParser import *
from PathHelper import *
import logging
import sys
from PathHelper import *
from compiler.LTLParser import LTLParser
from checker.Checker import Checker

# 同步command的单元测试


logger = logging.getLogger("syncunittest_logging")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

class TestSyncCommands(unittest.TestCase):

    def setUp(self):
        filepath = get_prism_model_dir() + get_sep() + "DPM4Prism.prism"
        self.model = ModelConstructor().parseModelFile(filepath)

    def test_parsing(self):
        # 测试解析成功
        self.assertEqual(self.model.model_type, ModelType.CTMC)
        logger.info("parsed commands")
        for module in self.model.modules.values():
            for comms in module.commands.values():
                if isinstance(comms, list):
                    for comm in comms:
                        logger.info("comm {} from module {}".format(comm.name, module.name))
                else:
                    logger.info("comm {} from module {}".format(comm.name, module.name))


    def test_checking(self):
        # 测试模型检测的成功,从而检测模型解析和SMC算法的正确性
        ltl = "true U<=10 failure"
        parsed_ltl = LTLParser().build_parser().parse_line(ltl)
        checker = Checker(model=self.model, ltl=parsed_ltl, duration=10.0)
        logger.info("checker'result is {}".format(checker.run_checker()))


