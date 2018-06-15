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
# logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "paths.log"))

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

    def test_gen_path(self):
        # 测试生成路径的正确性
        # 生成的路径要么总长为duration,要么出现failure

        # 结果:虽然测试通过,但是验证结果仍旧不同于PRISM(低于)

        failure_cnt = 0
        for _ in range(1000):
            self.model.duration = 10
            path = self.model.get_random_path_V2()
            for step in path:
                logger.info(step)
            logger.info("----------------")
            passed_time = path[-1].next_move.passed_time + path[-1].next_move.holding_time
            if set(["failure"]) in [step.ap_set for step in path]:
                failure_cnt += 1
                continue
            self.assertTrue(int(passed_time) >= 10)
        print "failure_cnt={}".format(failure_cnt)

    def test_checking(self):
        # 测试模型检测的成功,从而检测模型解析和SMC算法的正确性
        ltl = "true U<=10 failure"
        parsed_ltl = LTLParser().build_parser().parse_line(ltl)
        checker = Checker(model=self.model, ltl=parsed_ltl, duration=10.0)
        logger.info("checker'result is {}".format(checker.run_checker()))


