# -*- coding:utf-8 -*-
import unittest
from compiler.PRISMParser import *
import logging
from PathHelper import *
from compiler.LTLParser import LTLParser
from checker.Checker import Checker
from manager.Manager import Manager
from util.CsvFileHelper import parse_csv_cols
from itertools import product

# 同步command的单元测试


logger = logging.getLogger("syncunittest_logging")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(get_log_dir() + get_sep() + "paths.log"))


class TestSyncCommands(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()
        filepath = get_prism_model_dir() + get_sep() + "DPM.prism"
        self.manager.read_model_file(filepath)
        self.model = self.manager.model
        ltl = "true U<=10 failure"
        parsed_ltl = LTLParser().build_parser().parse_line(ltl)
        self.manager.set_manager_param_simple("duration", 10.0)
        self.checker = Checker(model=self.model, ltl=parsed_ltl, duration=10.0)
        self.manager.set_ltl(parsed_ltl)
        self.prism_x, self.prism_y = parse_csv_cols(get_prism_model_dir() + get_sep() + "Q_TRIGGER_1_20_1.csv")

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

        failure_cnt = 0

        for _ in range(5000):
            self.model.duration = 10
            path = self.model.get_random_path_V2()
            for step in path:
                logger.info(step)
            logger.info("----------------")
            passed_time = path[-1].next_move.passed_time + path[-1].next_move.holding_time
            if set(["failure"]) in [step.ap_set for step in path]:
                failure_cnt += 1
                continue
            if int(passed_time) < 10:
                failure = True
                for step in path:
                    logger.error(step)
                logger.error("-------------")
        print "failure_cnt={}".format(failure_cnt)

    def test_checking(self):
        # 测试模型检测的成功,从而检测模型解析和SMC算法的正确性
        logger.info("checker'result is {}".format(self.checker.run_checker()))

    def test_regression(self):
        constants = [("q_trigger", [v for v in range(1, 20, 2)])]
        self.manager.set_train_constants(*constants)
        self.manager.train_network()
        self.manager.set_test_xs([test_x for test_x in product(self.prism_x)])
        self.manager.run_test(prism_data_path=get_prism_model_dir() + get_sep() + "Q_TRIGGER_1_20_1.csv")

